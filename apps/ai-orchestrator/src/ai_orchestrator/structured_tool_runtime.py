from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Structured tool answer composition extracted from runtime.py.

This module is imported lazily from runtime.py after the shared helper surface is
already defined. It intentionally reuses the legacy runtime namespace during the
ongoing decomposition, so extracted functions keep behavior while the monolith
is split into focused modules.
"""

from . import runtime_core as _runtime_core


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


async def _compose_structured_tool_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    analysis_message: str,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
    public_plan_sink: dict[str, Any] | None = None,
    resolved_public_plan: PublicInstitutionPlan | None = None,
    prefer_fast_public_path: bool = False,
) -> str:
    message = request.message
    if request.telegram_chat_id is not None and actor is None:
        actor = await _fetch_actor_context(
            settings=settings, telegram_chat_id=request.telegram_chat_id
        )
    if _is_teacher_scope_guidance_query(
        message,
        actor=actor,
        user=request.user,
        conversation_context=conversation_context,
    ):
        if actor is not None and _should_fetch_teacher_schedule(
            message,
            actor=actor,
            user=request.user,
            conversation_context=conversation_context,
        ):
            return await _execute_teacher_protected_specialist(
                settings=settings,
                request=request,
                actor=actor,
                conversation_context=conversation_context,
            )
        return _compose_teacher_access_scope_answer(
            actor,
            school_name=str((school_profile or {}).get('school_name', 'Colegio Horizonte')),
        )
    if (
        actor is not None
        and (
            _is_access_scope_query(message)
            or _is_access_scope_repair_query(message, actor, conversation_context)
        )
        and not _should_prioritize_protected_sql_query(
            message,
            actor=actor,
            conversation_context=conversation_context,
        )
    ):
        return _compose_account_context_answer(
            actor,
            request_message=message,
            conversation_context=conversation_context,
        )
    if (
        actor is not None
        and request.telegram_chat_id is not None
        and (
            _looks_like_family_finance_aggregate_query(message)
            or _looks_like_family_attendance_aggregate_query(message)
            or _looks_like_family_academic_aggregate_query(message)
        )
    ):
        preview.mode = OrchestrationMode.structured_tool
        preview.needs_authentication = True
        return await _execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )
    if (
        school_profile is not None
        and preview.classification.access_tier is AccessTier.public
        and _base_profile_supports_fast_public_answer(
            message=request.message,
            profile=school_profile,
        )
    ):
        fast_public_channel_answer = _try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
                public_plan_sink['candidate_chosen'] = 'deterministic'
                public_plan_sink['candidate_reason'] = 'fast_public_channel_answer'
            return fast_public_channel_answer
    if (
        actor is not None
        and _is_student_focus_activation_query(message, actor)
        and not _should_continue_recent_student_task(
            message,
            actor=actor,
            conversation_context=conversation_context,
        )
    ):
        student = _student_focus_candidate(actor, message)
        student_name = str((student or {}).get('full_name', '')).strip() or None
        activated_answer = _compose_student_focus_activation_answer(
            actor,
            student_name=student_name,
        )
        if activated_answer:
            return activated_answer

    if preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}:
        orphan_workflow_follow_up = _compose_orphan_workflow_follow_up_answer(
            request.message,
            conversation_context,
        )
        if orphan_workflow_follow_up:
            return orphan_workflow_follow_up
        direct_canonical_lane = match_public_canonical_lane(
            analysis_message
        ) or match_public_canonical_lane(request.message)
        explicit_admin_query = looks_like_explicit_admin_status_query(
            request.message,
            authenticated=bool(request.user.authenticated),
        )
        if direct_canonical_lane and not explicit_admin_query:
            direct_canonical_answer = (
                compose_public_conduct_policy_contextual_answer(
                    request.message,
                    profile=school_profile,
                )
                if direct_canonical_lane == 'public_bundle.conduct_frequency_punctuality'
                else None
            ) or compose_public_canonical_lane_answer(direct_canonical_lane, profile=school_profile)
            if direct_canonical_answer:
                if public_plan_sink is not None:
                    public_plan_sink['deterministic_text'] = direct_canonical_answer
                return direct_canonical_answer
        use_admin_path = (
            request.telegram_chat_id is not None
            and preview.classification.access_tier is not AccessTier.public
            and (
                explicit_admin_query
                or _mentions_personal_admin_status(request.message)
                or _detect_admin_attribute_request(
                    request.message,
                    conversation_context=conversation_context,
                )
                is not None
                or _is_private_admin_follow_up(request.message, conversation_context)
            )
        )
        if preview.classification.domain is QueryDomain.institution and use_admin_path:
            if not {
                'get_administrative_status',
                'get_student_administrative_status',
                'get_actor_identity_context',
            } & set(preview.selected_tools):
                preview.selected_tools = [
                    *preview.selected_tools,
                    'get_administrative_status',
                    'get_student_administrative_status',
                ]
            if request.telegram_chat_id is None:
                return _compose_structured_deny(actor)
            actor = actor or await _fetch_actor_context(
                settings=settings, telegram_chat_id=request.telegram_chat_id
            )
            if actor is None:
                return _compose_structured_deny(actor)
            specialists = _build_protected_record_specialists(
                preview=preview,
                role_code=str(actor.get('role_code', 'anonymous')),
            )
            set_span_attributes(
                **{
                    'eduassist.protected_manager.executed_specialists': ','.join(
                        specialist.name for specialist in specialists
                    ),
                    'eduassist.protected_manager.executed_tools': ','.join(
                        tool_name
                        for specialist in specialists
                        for tool_name in specialist.tool_names
                    ),
                }
            )
            return await _execute_protected_records_specialist(
                settings=settings,
                request=request,
                preview=preview,
                actor=actor,
                conversation_context=conversation_context,
            )
        fast_public_channel_answer = None
        if _base_profile_supports_fast_public_answer(
            message=request.message,
            profile=school_profile,
        ):
            fast_public_channel_answer = _try_public_channel_fast_answer(
                message=request.message,
                profile=school_profile,
            )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
            return fast_public_channel_answer
        if prefer_fast_public_path:
            plan = resolved_public_plan or _build_public_institution_plan(
                request.message,
                list(preview.selected_tools),
                semantic_plan=None,
                conversation_context=conversation_context,
                school_profile=school_profile,
            )
        else:
            plan = resolved_public_plan or await _resolve_public_institution_plan(
                settings=settings,
                message=request.message,
                preview=preview,
                conversation_context=conversation_context,
                school_profile=school_profile,
            )
        if public_plan_sink is not None:
            public_plan_sink['plan'] = plan
        preview.selected_tools = list(plan.required_tools)
        profile, executed_tools, executed_specialists = await _execute_public_institution_plan(
            settings=settings,
            plan=plan,
            school_profile=school_profile,
        )
        should_prefer_deterministic_public_answer = (
            _is_positive_requirement_query(request.message)
            or _is_public_document_submission_query(request.message)
            or _is_comparative_query(request.message)
            or (
                (
                    _is_follow_up_query(request.message)
                    or _normalize_text(request.message).startswith('depois disso')
                )
                and any(
                    _message_matches_term(_normalize_text(request.message), term)
                    for term in {
                        'inicio das aulas',
                        'início das aulas',
                        'comecam as aulas',
                        'começam as aulas',
                        'aulas',
                    }
                )
                and (
                    _normalize_text(request.message).startswith('depois disso')
                    or _recent_user_message_mentions(
                        conversation_context,
                        {
                            'matricula',
                            'matrícula',
                            'proximo ciclo',
                            'próximo ciclo',
                            'inscricoes',
                            'inscrições',
                        },
                    )
                )
            )
            or any(
                _message_matches_term(_normalize_text(request.message), term)
                for term in {
                    'o que isso muda na pratica',
                    'o que isso muda na prática',
                    'na pratica no dia a dia',
                    'na prática no dia a dia',
                }
            )
            or plan.conversation_act in {'curriculum', 'comparative'}
        )
        llm_forced_mode = _llm_forced_mode_enabled(settings=settings, request=request)
        open_documentary_synthesis = _should_use_public_open_documentary_synthesis(
            request.message, plan
        )
        if (
            not llm_forced_mode
            and not open_documentary_synthesis
            and (prefer_fast_public_path or should_prefer_deterministic_public_answer)
            and profile
        ):
            deterministic_public_answer = _compose_public_profile_answer(
                profile,
                analysis_message,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=plan,
            )
            if deterministic_public_answer:
                if public_plan_sink is not None:
                    public_plan_sink['deterministic_text'] = deterministic_public_answer
                    public_plan_sink['candidate_chosen'] = 'deterministic'
                    public_plan_sink['candidate_reason'] = 'public_profile_deterministic_preferred'
                return deterministic_public_answer
        fast_public_channel_answer = None
        if not llm_forced_mode and not open_documentary_synthesis:
            fast_public_channel_answer = _try_public_channel_fast_answer(
                message=request.message,
                profile=profile,
            )
        if fast_public_channel_answer:
            if public_plan_sink is not None:
                public_plan_sink['deterministic_text'] = fast_public_channel_answer
                public_plan_sink['candidate_chosen'] = 'deterministic'
                public_plan_sink['candidate_reason'] = 'fast_public_channel_answer'
            return fast_public_channel_answer
        if (
            not llm_forced_mode
            and not open_documentary_synthesis
            and prefer_fast_public_path
            and profile
        ):
            deterministic_public_answer = _compose_public_profile_answer(
                profile,
                analysis_message,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=plan,
            )
            if deterministic_public_answer:
                if public_plan_sink is not None:
                    public_plan_sink['deterministic_text'] = deterministic_public_answer
                    public_plan_sink['candidate_chosen'] = 'deterministic'
                    public_plan_sink['candidate_reason'] = 'public_profile_deterministic_fast_path'
                return deterministic_public_answer
        canonical_lane = match_public_canonical_lane(request.message)
        evidence_bundle = (
            build_public_evidence_bundle(
                profile,
                primary_act=plan.conversation_act,
                secondary_acts=plan.secondary_acts,
                request_message=request.message,
                focus_hint=plan.focus_hint,
            )
            if profile
            else None
        )
        evidence_supports = [
            SimpleNamespace(label=fact.key, detail=fact.text, excerpt=fact.text)
            for fact in (evidence_bundle.facts if evidence_bundle is not None else ())
        ]
        probe_retrieval_search = None
        should_run_retrieval_probe = bool(
            getattr(settings, 'retrieval_aware_routing_enabled', True)
            and (
                canonical_lane is None
                or (llm_forced_mode and _looks_like_public_documentary_open_query(request.message))
            )
        )
        if should_run_retrieval_probe:
            try:
                retrieval_service = get_retrieval_service(
                    database_url=settings.database_url,
                    qdrant_url=settings.qdrant_url,
                    collection_name=settings.qdrant_documents_collection,
                    embedding_model=settings.document_embedding_model,
                    enable_query_variants=settings.retrieval_enable_query_variants,
                    enable_late_interaction_rerank=settings.retrieval_enable_late_interaction_rerank,
                    late_interaction_model=settings.retrieval_late_interaction_model,
                    candidate_pool_size=settings.retrieval_candidate_pool_size,
                    cheap_candidate_pool_size=settings.retrieval_cheap_candidate_pool_size,
                    deep_candidate_pool_size=settings.retrieval_deep_candidate_pool_size,
                    rerank_fused_weight=settings.retrieval_rerank_fused_weight,
                    rerank_late_interaction_weight=settings.retrieval_rerank_late_interaction_weight,
                )
                probe_retrieval_search = retrieval_service.hybrid_search(
                    query=analysis_message,
                    top_k=3,
                    visibility='public',
                    category='public_docs',
                    profile=RetrievalProfile.cheap,
                )
            except Exception:
                probe_retrieval_search = None
        probe = build_public_evidence_probe(
            message=request.message,
            canonical_lane=canonical_lane,
            primary_act=plan.conversation_act,
            secondary_acts=plan.secondary_acts,
            evidence_pack=SimpleNamespace(supports=evidence_supports)
            if evidence_supports
            else None,
            retrieval_search=probe_retrieval_search,
        )
        routing_decision = build_routing_decision(
            probe=probe,
            llm_forced_mode=llm_forced_mode,
        )
        telemetry_snapshot = get_stack_telemetry_snapshot('langgraph')
        serving_policy = build_public_serving_policy(
            settings=settings,
            stack_name='langgraph',
            request=request,
            probe=probe,
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
        if public_plan_sink is not None:
            public_plan_sink['retrieval_probe_topic'] = probe.topic
            public_plan_sink['routing_reason'] = routing_decision.reason
            public_plan_sink['serving_policy_reason'] = serving_policy.reason
            public_plan_sink['retrieval_probe_hit_count'] = probe.hit_count
            public_plan_sink['retrieval_probe_topic_match_score'] = probe.topic_match_score

        if (
            public_plan_sink is not None
            and getattr(settings, 'public_response_cache_enabled', True)
            and serving_policy.prefer_cache
        ):
            semantic_threshold = float(
                getattr(settings, 'public_response_semantic_jaccard_threshold', 0.84)
                if getattr(settings, 'public_response_semantic_cache_enabled', True)
                else 1.01
            )
            cached_public_response = get_cached_public_response(
                message=request.message,
                canonical_lane=canonical_lane,
                topic=probe.topic,
                evidence_fingerprint=probe.evidence_fingerprint,
                semantic_threshold=semantic_threshold,
            )
            if cached_public_response is not None:
                public_plan_sink['response_cache_hit'] = True
                public_plan_sink['response_cache_kind'] = cached_public_response.cache_kind
                public_plan_sink['candidate_chosen'] = (
                    cached_public_response.candidate_kind or 'deterministic'
                )
                public_plan_sink['candidate_reason'] = (
                    f'cache:{cached_public_response.reason or cached_public_response.cache_kind}'
                )
                public_plan_sink['deterministic_text'] = cached_public_response.text
                return cached_public_response.text

        slot_memory = _build_conversation_slot_memory(
            actor=actor,
            profile=profile,
            conversation_context=conversation_context,
            request_message=request.message,
            public_plan=plan,
            preview=preview,
        )
        set_span_attributes(
            **{
                'eduassist.public_manager.act': plan.conversation_act,
                'eduassist.public_manager.secondary_acts': ','.join(plan.secondary_acts),
                'eduassist.public_manager.fetch_profile': plan.fetch_profile,
                'eduassist.public_manager.semantic_source': plan.semantic_source,
                'eduassist.public_manager.focus_hint': plan.focus_hint or '',
                'eduassist.public_manager.requested_attribute': plan.requested_attribute or '',
                'eduassist.public_manager.requested_channel': plan.requested_channel or '',
                'eduassist.public_manager.slot_focus_kind': slot_memory.focus_kind or '',
                'eduassist.public_manager.slot_contact_subject': slot_memory.contact_subject or '',
                'eduassist.public_manager.slot_feature_key': slot_memory.feature_key or '',
                'eduassist.public_manager.executed_tools': ','.join(executed_tools),
                'eduassist.public_manager.executed_specialists': ','.join(executed_specialists),
                'eduassist.public_manager.routing_probe_topic': probe.topic or '',
                'eduassist.public_manager.routing_reason': routing_decision.reason,
                'eduassist.public_manager.serving_policy_reason': serving_policy.reason,
            }
        )
        if not profile and plan.conversation_act != 'utility_date':
            return _compose_public_gap_answer(set())

        deterministic_candidate = build_response_candidate(
            kind='deterministic',
            text=_compose_public_profile_answer(
                profile,
                analysis_message,
                actor=actor,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=plan,
            ),
            reason='public_profile_deterministic',
            used_llm=False,
            retrieval_backend=RetrievalBackend.none,
            selected_tools=tuple(preview.selected_tools),
            source_count=probe.source_count,
            support_count=probe.support_count,
        )
        documentary_candidate = None
        if (
            getattr(settings, 'candidate_chooser_enabled', True)
            and routing_decision.allow_documentary_synthesis
            and serving_policy.allow_documentary_synthesis
        ):
            agentic_sink: dict[str, Any] = {}
            documentary_text = await _compose_public_profile_answer_agentic(
                settings=settings,
                profile=profile,
                actor=actor,
                message=analysis_message,
                original_message=request.message,
                conversation_context=conversation_context,
                semantic_plan=plan,
                deterministic_text_sink=agentic_sink,
            )
            documentary_candidate = build_response_candidate(
                kind='documentary_synthesis',
                text=documentary_text,
                reason='public_open_documentary_synthesis',
                used_llm=bool(agentic_sink.get('agentic_llm_used')),
                llm_stages=tuple(agentic_sink.get('agentic_llm_stages', [])),
                retrieval_backend=RetrievalBackend.none,
                selected_tools=tuple(preview.selected_tools),
                source_count=probe.source_count,
                support_count=probe.support_count,
            )

        chosen_candidate = None
        candidates = [
            candidate
            for candidate in [deterministic_candidate, documentary_candidate]
            if candidate is not None
        ]
        if getattr(settings, 'candidate_chooser_enabled', True):
            chosen_candidate = choose_best_candidate(
                candidates=candidates,
                probe=probe,
                policy=serving_policy,
            )
        if chosen_candidate is None and candidates:
            fallback_candidate = (
                documentary_candidate
                if (documentary_candidate is not None and not routing_decision.prefer_deterministic)
                else deterministic_candidate
            )
            if fallback_candidate is not None:
                chosen_candidate = SimpleNamespace(
                    candidate=fallback_candidate,
                    chooser_reason='single_candidate_fallback',
                )
        if chosen_candidate is not None:
            chosen_text = chosen_candidate.candidate.text
            if public_plan_sink is not None:
                public_plan_sink['candidate_chosen'] = chosen_candidate.candidate.kind
                public_plan_sink['candidate_reason'] = (
                    getattr(chosen_candidate, 'chooser_reason', '')
                    or chosen_candidate.candidate.reason
                )
                public_plan_sink['response_cache_hit'] = False
                public_plan_sink['response_cache_kind'] = None
                if chosen_candidate.candidate.used_llm:
                    public_plan_sink['agentic_llm_used'] = True
                    public_plan_sink['agentic_llm_stages'] = list(
                        chosen_candidate.candidate.llm_stages
                    )
                if chosen_candidate.candidate.kind == 'deterministic':
                    public_plan_sink['deterministic_text'] = chosen_text
                if (
                    getattr(settings, 'public_response_cache_enabled', True)
                    and serving_policy.prefer_cache
                    and chosen_candidate.candidate.cacheable
                ):
                    store_cached_public_response(
                        message=request.message,
                        text=chosen_text,
                        canonical_lane=canonical_lane,
                        topic=probe.topic,
                        evidence_fingerprint=probe.evidence_fingerprint,
                        candidate_kind=chosen_candidate.candidate.kind,
                        reason=getattr(chosen_candidate, 'chooser_reason', '')
                        or chosen_candidate.candidate.reason,
                        ttl_seconds=float(
                            getattr(settings, 'public_response_cache_ttl_seconds', 300.0)
                        ),
                    )
            return chosen_text

        return await _compose_public_profile_answer_agentic(
            settings=settings,
            profile=profile,
            actor=actor,
            message=analysis_message,
            original_message=request.message,
            conversation_context=conversation_context,
            semantic_plan=plan,
            deterministic_text_sink=public_plan_sink,
        )

    if preview.classification.domain is QueryDomain.support:
        if 'get_workflow_status' in preview.selected_tools:
            workflow_specialist = 'workflow_status'
        elif 'update_visit_booking' in preview.selected_tools:
            workflow_specialist = 'workflow_visit_update'
        elif 'update_institutional_request' in preview.selected_tools:
            workflow_specialist = 'workflow_request_update'
        else:
            workflow_specialist = 'workflow'
        set_span_attributes(
            **{
                'eduassist.workflow_manager.executed_specialists': workflow_specialist,
            }
        )
        if 'get_workflow_status' in preview.selected_tools:
            conversation_external_id = request.conversation_id or _effective_conversation_id(
                request
            )
            if not conversation_external_id:
                return (
                    'Consigo acompanhar protocolos por aqui, mas preciso que a conversa esteja vinculada '
                    'ao atendimento atual. Se quiser, me envie o codigo que comeca com VIS, REQ ou ATD.'
                )
            protocol_code_hint = _extract_protocol_code_hint(request.message, conversation_context)
            workflow_kind_hint = _detect_workflow_kind_hint(request.message, conversation_context)
            set_span_attributes(
                **{
                    'eduassist.workflow_manager.protocol_hint_present': bool(protocol_code_hint),
                    'eduassist.workflow_manager.workflow_kind_hint': workflow_kind_hint,
                }
            )
            cached_workflow_payload = _workflow_snapshot_from_context(
                conversation_context,
                workflow_kind_hint=workflow_kind_hint,
                protocol_code_hint=protocol_code_hint,
            )
            if isinstance(cached_workflow_payload, dict):
                set_span_attributes(
                    **{
                        'eduassist.workflow_manager.cache_hit': True,
                    }
                )
                return _compose_workflow_status_answer(
                    cached_workflow_payload,
                    protocol_code_hint=protocol_code_hint,
                    request_message=request.message,
                )
            set_span_attributes(
                **{
                    'eduassist.workflow_manager.cache_hit': False,
                }
            )
            workflow_payload = await _fetch_internal_workflow_status(
                settings=settings,
                conversation_external_id=conversation_external_id,
                protocol_code=protocol_code_hint,
                workflow_kind=workflow_kind_hint,
            )
            return _compose_workflow_status_answer(
                workflow_payload,
                protocol_code_hint=protocol_code_hint,
                request_message=request.message,
            )
        if 'update_visit_booking' in preview.selected_tools:
            if (
                _detect_visit_booking_action(request.message) == 'reschedule'
                and _extract_requested_date(request.message) is None
                and not _extract_requested_window(request.message)
            ):
                cached_workflow_payload = _workflow_snapshot_from_context(
                    conversation_context,
                    workflow_kind_hint='visit_booking',
                    protocol_code_hint=_extract_protocol_code_hint(
                        request.message, conversation_context
                    ),
                )
                if isinstance(cached_workflow_payload, dict):
                    return _compose_visit_booking_action_answer(
                        cached_workflow_payload,
                        request_message=request.message,
                    )
                conversation_external_id = request.conversation_id or _effective_conversation_id(
                    request
                )
                if conversation_external_id:
                    live_workflow_payload = await _fetch_internal_workflow_status(
                        settings=settings,
                        conversation_external_id=conversation_external_id,
                        protocol_code=_extract_protocol_code_hint(
                            request.message, conversation_context
                        ),
                        workflow_kind='visit_booking',
                    )
                    if isinstance(live_workflow_payload, dict):
                        return _compose_visit_booking_action_answer(
                            live_workflow_payload,
                            request_message=request.message,
                        )
            workflow_payload = await _update_visit_booking(
                settings=settings,
                request=request,
                conversation_context=conversation_context,
            )
            return _compose_visit_booking_action_answer(
                workflow_payload,
                request_message=request.message,
            )
        if 'update_institutional_request' in preview.selected_tools:
            workflow_payload = await _update_institutional_request(
                settings=settings,
                request=request,
                conversation_context=conversation_context,
            )
            return _compose_institutional_request_action_answer(
                workflow_payload,
                request_message=request.message,
            )
        if 'schedule_school_visit' in preview.selected_tools:
            workflow_payload = await _create_visit_booking(
                settings=settings,
                request=request,
                actor=actor,
            )
            return _compose_visit_booking_answer(workflow_payload, school_profile)
        workflow_payload = await _create_institutional_request(
            settings=settings,
            request=request,
            actor=actor,
        )
        return _compose_institutional_request_answer(workflow_payload)

    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    actor = actor or await _fetch_actor_context(
        settings=settings, telegram_chat_id=request.telegram_chat_id
    )
    if actor is None:
        return _compose_structured_deny(actor)

    role_code = str(actor.get('role_code', 'anonymous'))

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        specialists = _build_protected_record_specialists(preview=preview, role_code=role_code)
        set_span_attributes(
            **{
                'eduassist.protected_manager.executed_specialists': ','.join(
                    specialist.name for specialist in specialists
                ),
                'eduassist.protected_manager.executed_tools': ','.join(
                    tool_name for specialist in specialists for tool_name in specialist.tool_names
                ),
            }
        )
        return await _execute_teacher_protected_specialist(
            settings=settings,
            request=request,
            actor=actor,
            conversation_context=conversation_context,
        )

    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        if _is_student_focus_activation_query(
            message, actor
        ) and not _should_continue_recent_student_task(
            message,
            actor=actor,
            conversation_context=conversation_context,
        ):
            student = _student_focus_candidate(actor, message)
            student_name = str((student or {}).get('full_name', '')).strip() or None
            activated_answer = _compose_student_focus_activation_answer(
                actor,
                student_name=student_name,
            )
            if activated_answer:
                return activated_answer
        specialists = _build_protected_record_specialists(preview=preview, role_code=role_code)
        set_span_attributes(
            **{
                'eduassist.protected_manager.executed_specialists': ','.join(
                    specialist.name for specialist in specialists
                ),
                'eduassist.protected_manager.executed_tools': ','.join(
                    tool_name for specialist in specialists for tool_name in specialist.tool_names
                ),
            }
        )
        return await _execute_protected_records_specialist(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )

    return (
        'Esse fluxo protegido ainda nao foi concluido para este perfil no Telegram. '
        'Por enquanto, use o portal autenticado da escola.'
    )
