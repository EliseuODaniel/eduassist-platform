from __future__ import annotations

from typing import Any, Callable

from . import runtime as rt
from .python_functions_kernel import KernelPlan, KernelReflection, KernelRunResult, build_kernel_plan
from .evidence_pack import (
    build_direct_answer_evidence_pack,
    build_known_unknown_evidence_pack,
    build_retrieval_evidence_pack,
    build_structured_tool_evidence_pack,
)
from .final_polish_policy import build_final_polish_decision
from .graph_rag_runtime import run_graph_rag_query
from .models import (
    AccessTier,
    MessageResponse,
    MessageEvidencePack,
    MessageEvidenceSupport,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    QueryDomain,
    RetrievalBackend,
)
from .path_profiles import PathExecutionProfile, get_path_execution_profile
from .python_functions_public_knowledge import compose_public_canonical_lane_answer, match_public_canonical_lane
from .python_functions_public_known_unknowns import detect_public_known_unknown_key, resolve_public_known_unknown_answer
from .python_functions_local_llm import (
    compose_python_functions_with_provider,
    polish_python_functions_with_provider,
    revise_python_functions_with_provider,
    verify_python_functions_answer_against_contract,
)
from .python_functions_retrieval import get_retrieval_service
from .python_functions_retrieval import (
    can_read_restricted_documents,
    compose_restricted_document_grounded_answer_for_query,
    compose_restricted_document_no_match_answer,
    looks_like_restricted_document_query,
    select_relevant_restricted_hits,
)


def _mode_priority(mode: OrchestrationMode) -> int:
    priorities = {
        OrchestrationMode.structured_tool: 5,
        OrchestrationMode.handoff: 4,
        OrchestrationMode.graph_rag: 3,
        OrchestrationMode.hybrid_retrieval: 3,
        OrchestrationMode.clarify: 1,
        OrchestrationMode.deny: 0,
    }
    return priorities.get(mode, 0)


def _needs_contextual_replan(*, request: MessageResponseRequest, plan: KernelPlan, analysis_message: str) -> bool:
    if analysis_message.strip() == str(request.message).strip():
        return False
    if rt._is_follow_up_query(request.message):
        return True
    if plan.preview.mode in {OrchestrationMode.clarify, OrchestrationMode.deny}:
        return True
    return bool(plan.preview.classification.domain in {QueryDomain.institution, QueryDomain.finance, QueryDomain.academic})


def _select_better_plan(*, current: KernelPlan, candidate: KernelPlan) -> KernelPlan:
    current_priority = _mode_priority(current.preview.mode)
    candidate_priority = _mode_priority(candidate.preview.mode)
    if candidate_priority > current_priority:
        return candidate
    if candidate_priority == current_priority:
        current_tools = tuple(current.preview.selected_tools)
        candidate_tools = tuple(candidate.preview.selected_tools)
        if candidate_tools and candidate_tools != current_tools:
            return candidate
        if candidate.preview.reason != current.preview.reason:
            return candidate
    return current


def _should_prefer_contextual_tie(*, request: MessageResponseRequest, current: KernelPlan, candidate: KernelPlan) -> bool:
    if not rt._is_follow_up_query(request.message):
        return False
    if candidate.preview.mode != current.preview.mode:
        return False
    return candidate.preview.mode in {
        OrchestrationMode.structured_tool,
        OrchestrationMode.handoff,
        OrchestrationMode.hybrid_retrieval,
    }


def _message_requests_academic_domain(message: str) -> bool:
    normalized = rt._normalize_text(message)
    academic_terms = {
        *rt.GRADE_TERMS,
        *rt.ATTENDANCE_TERMS,
        *rt.GRADE_REQUIREMENT_TERMS,
        *rt.GRADE_APPROVAL_TERMS,
    }
    return any(rt._message_matches_term(normalized, term) for term in academic_terms)


def _message_requests_finance_domain(message: str) -> bool:
    normalized = rt._normalize_text(message)
    finance_terms = {
        'financeiro',
        'mensalidade',
        'mensalidades',
        'pagamento',
        'pagamentos',
        'boleto',
        'boletos',
        'fatura',
        'faturas',
        'em aberto',
        'vencida',
        'vencidas',
    }
    return any(rt._message_matches_term(normalized, term) for term in finance_terms)


def _message_mentions_library_entity(message: str) -> bool:
    normalized = rt._normalize_text(message)
    return any(
        rt._message_matches_term(normalized, term)
        for term in {'biblioteca', 'library', 'acervo', 'biblioteca aurora'}
    )


def _message_switches_public_entity_away_from_library(message: str) -> bool:
    normalized = rt._normalize_text(message)
    non_library_terms = {
        'diretor',
        'diretora',
        'direcao',
        'direção',
        'diretoria',
        'alunos',
        'salas',
        'turno',
        'turnos',
        'turma',
        'turmas',
        'cantina',
        'cardapio',
        'cardápio',
        'bolsa',
        'idade minima',
        'idade mínima',
        'mensalidade',
        'quadra',
        'professores',
        'secretaria',
    }
    return any(rt._message_matches_term(normalized, term) for term in non_library_terms)


def _maybe_explicit_domain_override_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    current: KernelPlan,
    replan_builder: Callable[[MessageResponseRequest, Any, str], KernelPlan] | None = None,
) -> KernelPlan | None:
    if not request.user.authenticated:
        return None
    requested_domain: QueryDomain | None = None
    if _message_requests_academic_domain(request.message):
        requested_domain = QueryDomain.academic
    elif _message_requests_finance_domain(request.message):
        requested_domain = QueryDomain.finance
    if requested_domain is None or current.preview.classification.domain is requested_domain:
        return None

    if replan_builder is not None:
        candidate = replan_builder(request, settings, current.mode)
    else:
        candidate = build_kernel_plan(
            request=request,
            settings=settings,
            stack_name=current.stack_name,
            mode=current.mode,
        )
    if candidate.preview.classification.domain is not requested_domain:
        return None
    return candidate.model_copy(
        update={
            'plan_notes': [*current.plan_notes, f'explicit_domain_override:{requested_domain.value}'],
        }
    )


def _with_repair_ack(*, request_message: str, answer_text: str) -> str:
    normalized = rt._normalize_text(request_message)
    if not any(
        marker in normalized
        for marker in (
            'mudei de ideia',
            'na verdade',
            'corrigindo',
            'melhor',
            'quero secretaria',
            'quero financeiro',
        )
    ):
        return answer_text
    lowered_answer = answer_text.casefold()
    if any(marker in lowered_answer for marker in ('certo', 'ajustei', 'sem problema', 'corrigi')):
        return answer_text
    return f'Sem problema, ajustei isso por aqui.\n\n{answer_text}'


async def _maybe_contextual_public_direct_answer(
    *,
    request: MessageResponseRequest,
    analysis_message: str,
    preview: Any,
    settings: Any,
    school_profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if rt._llm_forced_mode_enabled(settings=settings, request=request):
        return None
    public_boundary_answer = rt._compose_contextual_public_boundary_answer(
        message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if public_boundary_answer:
        return public_boundary_answer
    timeline_followup_answer = rt._compose_contextual_public_timeline_followup_answer(
        request_message=request.message,
        conversation_context=conversation_context,
        profile=school_profile,
    )
    if timeline_followup_answer:
        return timeline_followup_answer
    analysis_canonical_lane = match_public_canonical_lane(analysis_message)
    rewritten_public_followup = analysis_message.strip() != str(request.message).strip() and (
        analysis_canonical_lane is not None or rt._is_public_timeline_query(analysis_message)
    )
    is_public_context = (
        preview.classification.access_tier is AccessTier.public
        or not request.user.authenticated
        or rewritten_public_followup
    )
    if not is_public_context:
        return None

    contextual_public_message = (
        rt._contextualize_public_followup_message(
            request_message=request.message,
            analysis_message=analysis_message,
            conversation_context=conversation_context,
        )
        if rewritten_public_followup
        else request.message
    )
    if rt._is_direct_service_routing_bundle_query(contextual_public_message):
        return rt._compose_service_routing_answer(
            school_profile,
            contextual_public_message,
            conversation_context=conversation_context,
        )
    if rt._should_prefer_raw_public_followup_message(
        request_message=request.message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    ) and rewritten_public_followup and str(contextual_public_message).strip() == str(analysis_message).strip() and not rt._must_preserve_contextual_public_followup_message(
        request_message=request.message,
        conversation_context=conversation_context,
    ):
        contextual_public_message = request.message
    prefer_fast_public_direct = (
        rewritten_public_followup
        or rt._is_service_routing_query(request.message)
        or rt._has_public_multi_intent_signal(request.message)
        or rt._is_public_timeline_query(request.message)
        or rt._is_public_timeline_lifecycle_query(request.message)
        or rt._is_public_year_three_phase_query(request.message)
        or rt._is_access_scope_query(request.message)
    )
    if (
        prefer_fast_public_direct
        and rt._base_profile_supports_fast_public_answer(
            message=contextual_public_message,
            profile=school_profile,
        )
    ):
        fast_public_answer = rt._try_public_channel_fast_answer(
            message=contextual_public_message,
            profile=school_profile,
        )
        if fast_public_answer:
            return fast_public_answer

    canonical_lane = analysis_canonical_lane or match_public_canonical_lane(request.message)
    if canonical_lane:
        canonical_answer = compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
        if canonical_answer:
            if request.user.authenticated and rewritten_public_followup and rt._message_matches_term(rt._normalize_text(request.message), 'apenas o que e publico nesse tema'):
                return (
                    'Sobre esse tema, eu continuo sem acesso ao protocolo interno; '
                    f'so posso trazer o que e publico. {canonical_answer}'
                )
            return canonical_answer

    fast_public_answer = None
    if rt._base_profile_supports_fast_public_answer(
        message=request.message,
        profile=school_profile,
    ):
        fast_public_answer = rt._try_public_channel_fast_answer(
            message=request.message,
            profile=school_profile,
        )
    if fast_public_answer:
        return fast_public_answer

    if rt._is_public_timeline_query(request.message):
        timeline = await rt._fetch_public_timeline(settings=settings)
        entries = timeline.get('entries') if isinstance(timeline, dict) else None
        if isinstance(entries, list) and entries:
            timeline_profile = dict(school_profile)
            timeline_profile['public_timeline'] = entries
            context = rt._build_public_profile_context(
                timeline_profile,
                request.message,
                conversation_context=conversation_context,
            )
            timeline_answer = rt._handle_public_timeline(context)
            if isinstance(timeline_answer, str) and timeline_answer.strip():
                return timeline_answer

    normalized_request = rt._normalize_text(request.message)
    normalized_analysis = rt._normalize_text(analysis_message)
    recent_context_lines = [rt._normalize_text(content) for _, content in rt._recent_message_lines(conversation_context)]
    recent_context_mentions_library = any('biblioteca' in content or 'biblioteca aurora' in content for content in recent_context_lines)
    current_message_mentions_library = _message_mentions_library_entity(request.message)
    current_message_mentions_leadership = any(
        rt._message_matches_term(normalized_request, term)
        for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}
    )
    library_name_followup_terms = {
        'como ela se chama',
        'como se chama',
        'qual o nome dela',
        'nome dela',
        'nome da biblioteca',
        'qual o nome da biblioteca',
    }
    library_hours_followup_terms = {
        'ate que horas funciona',
        'até que horas funciona',
        'horario',
        'horário',
        'funciona',
    }
    library_followup_referents = {'ela', 'dela', 'biblioteca', 'da biblioteca'}

    wants_document_path = rt._is_public_document_submission_query(analysis_message) or (
        any(
            rt._message_matches_term(normalized_analysis, term)
            for term in {'documentacao', 'documentação', 'documentos', 'cadastro'}
        )
        and any(
            rt._message_matches_term(normalized_analysis, term)
            for term in {'mandar', 'enviar', 'envio', 'caminho'}
        )
    )
    if wants_document_path:
        return rt._compose_public_document_submission_answer(school_profile, message=analysis_message)

    asks_library_name_and_hours = (
        (
            (
                current_message_mentions_library
                and any(
                    rt._message_matches_term(normalized_request, term)
                    for term in {
                        'como ela se chama',
                        'qual o nome da biblioteca',
                        'nome da biblioteca',
                        'ate que horas funciona',
                        'até que horas funciona',
                        'horario da biblioteca',
                        'horário da biblioteca',
                        'funciona',
                    }
                )
            )
            or (
                recent_context_mentions_library
                and rt._is_follow_up_query(request.message)
                and not current_message_mentions_leadership
                and not _message_switches_public_entity_away_from_library(request.message)
                and (
                    (
                        any(rt._message_matches_term(normalized_request, term) for term in library_name_followup_terms)
                        and any(rt._message_matches_term(normalized_request, term) for term in library_followup_referents)
                    )
                    or any(rt._message_matches_term(normalized_request, term) for term in library_hours_followup_terms)
                )
            )
        )
    )
    if asks_library_name_and_hours:
        return 'A biblioteca se chama Biblioteca Aurora e funciona de segunda a sexta, das 7h30 as 18h00.'

    asks_school_year_start = (
        any(
            rt._message_matches_term(normalized_request, term)
            for term in {'aulas', 'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas'}
        )
        and (
            normalized_request.startswith('depois disso')
            or rt._is_follow_up_query(request.message)
            or any(
                rt._message_matches_term(normalized_analysis, term)
                for term in {'matricula', 'matrícula', 'inscricoes', 'inscrições', 'ano que vem', 'proximo ciclo', 'próximo ciclo'}
            )
            or any(
                any(
                    rt._message_matches_term(content, term)
                    for term in {'matricula', 'matrícula', 'inscricoes', 'inscrições', 'ano que vem', 'proximo ciclo', 'próximo ciclo'}
                )
                for content in recent_context_lines
            )
        )
    )
    if asks_school_year_start:
        timeline = await rt._fetch_public_timeline(settings=settings)
        entries = timeline.get('entries') if isinstance(timeline, dict) else None
        if isinstance(entries, list):
            for item in entries:
                if not isinstance(item, dict):
                    continue
                if 'school_year_start' not in str(item.get('topic_key', '')):
                    continue
                summary = str(item.get('summary', '')).strip()
                notes = str(item.get('notes', '')).strip()
                if summary and notes:
                    return f'{summary} {notes}'.strip()
                if summary:
                    return summary

    return None


def _maybe_public_unpublished_direct_answer(
    *,
    request: MessageResponseRequest,
    preview: Any,
) -> str | None:
    is_public_context = preview.classification.access_tier is AccessTier.public or not request.user.authenticated
    if not is_public_context:
        return None
    return resolve_public_known_unknown_answer(request.message)


def _maybe_hypothetical_public_pricing_answer(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
    preview: Any,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> tuple[str, Any] | None:
    if not isinstance(school_profile, dict):
        return None
    if preview.classification.access_tier is not AccessTier.public:
        return None
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return None
    if not plan.entities.is_hypothetical or not plan.entities.quantity_hint:
        return None
    if not (
        plan.entities.domain_hint == 'public_pricing'
        or rt._is_explicit_public_pricing_projection_query(
            request.message,
            conversation_context=conversation_context,
        )
    ):
        return None

    public_plan = rt._build_public_institution_plan(
        request.message,
        list(preview.selected_tools),
        semantic_plan=None,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    if public_plan.conversation_act != 'pricing':
        public_plan = rt.replace(
            public_plan,
            conversation_act='pricing',
            secondary_acts=(),
        )
    answer = rt._compose_public_profile_answer(
        school_profile,
        request.message,
        actor=None,
        original_message=request.message,
        conversation_context=conversation_context,
        semantic_plan=public_plan,
    )
    if str(plan.entities.quantity_hint) not in answer or 'R$' not in answer:
        return None
    return answer, public_plan


def _build_kernel_evidence_pack(
    *,
    request: MessageResponseRequest,
    plan: KernelPlan,
    preview: Any,
    selected_tools: list[str],
    citations: list[MessageResponseCitation],
    school_profile: dict[str, Any] | None,
    has_known_unknown_answer: bool,
) -> MessageEvidencePack | None:
    school_name = str((school_profile or {}).get('name') or 'Colegio Horizonte').strip()
    if has_known_unknown_answer:
        return build_known_unknown_evidence_pack(
            requested_key=detect_public_known_unknown_key(request.message),
            selected_tools=selected_tools,
            school_name=school_name,
        )
    if citations:
        return build_retrieval_evidence_pack(
            citations=citations,
            selected_tools=selected_tools,
            retrieval_backend=preview.retrieval_backend if isinstance(preview.retrieval_backend, RetrievalBackend) else RetrievalBackend.none,
            summary='Resposta grounded no kernel compartilhado com retrieval e citacoes.',
        )
    if preview.mode is OrchestrationMode.structured_tool:
        return build_structured_tool_evidence_pack(
            selected_tools=selected_tools,
            slice_name=plan.slice_name,
            summary=(
                'Resposta grounded em tool-first do kernel compartilhado.'
                if selected_tools
                else 'Resposta grounded em fatos publicos estruturados do kernel compartilhado.'
            ),
        )
    if preview.mode is OrchestrationMode.hybrid_retrieval and str(preview.reason).startswith('kernel_public_canonical_lane:'):
        lane_name = str(preview.reason).split(':', 1)[1].strip() or 'bundle_documental_publico'
        return build_direct_answer_evidence_pack(
            summary='Resposta canônica grounded em um bundle documental público conhecido.',
            supports=[
                MessageEvidenceSupport(
                    kind='canonical_lane',
                    label=lane_name,
                    detail='Lane canônica pública selecionada antes do retrieval pesado.',
                )
            ],
        )
    if preview.mode in {OrchestrationMode.clarify, OrchestrationMode.deny}:
        return build_direct_answer_evidence_pack(
            strategy=preview.mode.value,
            summary='Resposta emitida pelo contrato de seguranca do kernel compartilhado.',
            supports=[
                MessageEvidenceSupport(
                    kind='contract',
                    label=preview.mode.value,
                    detail=preview.reason,
                )
            ],
        )
    return None


async def execute_kernel_plan(
    *,
    request: MessageResponseRequest,
    settings: Any,
    plan: KernelPlan,
    engine_name: str,
    engine_mode: str,
    path_profile: PathExecutionProfile | None = None,
    replan_builder: Callable[[MessageResponseRequest, Any, str], KernelPlan] | None = None,
) -> KernelRunResult:
    effective_path_profile = path_profile or get_path_execution_profile(engine_name)
    prefer_fast_public_path = effective_path_profile.prefer_fast_public_path
    actor = await rt._fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_conversation_id = rt._effective_conversation_id(request)
    conversation_context = await rt._fetch_conversation_context(
        settings=settings,
        conversation_external_id=effective_conversation_id,
        channel=request.channel.value,
    )
    context_payload = rt._conversation_context_payload(conversation_context)
    analysis_message = rt._build_analysis_message(request.message, conversation_context)
    school_profile = await rt._fetch_public_school_profile(settings=settings)
    effective_plan = plan
    if effective_path_profile.use_contextual_replan and _needs_contextual_replan(
        request=request,
        plan=plan,
        analysis_message=analysis_message,
    ):
        contextual_request = request.model_copy(update={'message': analysis_message})
        if replan_builder is not None:
            candidate_plan = replan_builder(contextual_request, settings, plan.mode)
        else:
            candidate_plan = build_kernel_plan(
                request=contextual_request,
                settings=settings,
                stack_name=plan.stack_name,
                mode=plan.mode,
            )
        effective_plan = _select_better_plan(current=plan, candidate=candidate_plan)
        if effective_plan is plan and _should_prefer_contextual_tie(request=request, current=plan, candidate=candidate_plan):
            effective_plan = candidate_plan
        if effective_plan is candidate_plan:
            effective_plan = candidate_plan.model_copy(
                update={
                    'plan_notes': [*plan.plan_notes, 'contextual_replan'],
                }
            )
    explicit_domain_override = _maybe_explicit_domain_override_plan(
        request=request,
        settings=settings,
        current=effective_plan,
        replan_builder=replan_builder,
    )
    if explicit_domain_override is not None:
        effective_plan = explicit_domain_override
    preview = effective_plan.preview.model_copy(deep=True)
    if actor is not None and request.user.authenticated:
        rt._apply_protected_domain_rescue(
            preview=preview,
            actor=actor,
            message=request.message,
            conversation_context=context_payload,
        )

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    visual_assets = []
    calendar_events = []
    retrieval_context_pack: str | None = None
    public_plan = None
    deterministic_fallback_text: str | None = None
    query_hints: set[str] = set()
    semantic_judge_used = False
    llm_stages: list[str] = []
    answer_verifier_fallback_used = False
    contextual_public_answer = await _maybe_contextual_public_direct_answer(
        request=request,
        analysis_message=analysis_message,
        preview=preview,
        settings=settings,
        school_profile=school_profile,
        conversation_context=context_payload,
    )
    unpublished_public_answer = _maybe_public_unpublished_direct_answer(
        request=request,
        preview=preview,
    )
    hypothetical_public_pricing_direct = _maybe_hypothetical_public_pricing_answer(
        request=request,
        plan=effective_plan,
        preview=preview,
        school_profile=school_profile,
        conversation_context=context_payload,
    )

    if contextual_public_answer:
        message_text = contextual_public_answer
        deterministic_fallback_text = contextual_public_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'contextual_public_direct_answer',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            }
        )
    elif unpublished_public_answer:
        message_text = unpublished_public_answer
        deterministic_fallback_text = unpublished_public_answer
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'public_unpublished_fact_direct_answer',
                'selected_tools': list(dict.fromkeys([*preview.selected_tools, 'get_public_school_profile'])),
            }
        )
    elif hypothetical_public_pricing_direct:
        message_text, public_plan = hypothetical_public_pricing_direct
        deterministic_fallback_text = message_text
        preview = preview.model_copy(
            update={
                'mode': OrchestrationMode.structured_tool,
                'reason': 'hypothetical_public_pricing_direct_answer',
                'selected_tools': list(
                    dict.fromkeys([*preview.selected_tools, 'get_public_school_profile', 'project_public_pricing'])
                ),
            }
        )
    elif preview.mode is OrchestrationMode.structured_tool:
        public_plan_sink: dict[str, Any] = {}
        resolved_public_plan = None
        if (
            preview.classification.access_tier is AccessTier.public
            and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
            and analysis_message.strip() != str(request.message).strip()
        ):
            try:
                resolved_public_plan = await rt._resolve_public_institution_plan(
                    settings=settings,
                    message=analysis_message,
                    preview=preview,
                    conversation_context=context_payload,
                    school_profile=school_profile,
                )
            except Exception:
                resolved_public_plan = None
        message_text = await rt._compose_structured_tool_answer(
            settings=settings,
            request=request,
            analysis_message=analysis_message,
            preview=preview,
            actor=actor,
            school_profile=school_profile,
            conversation_context=context_payload,
            public_plan_sink=public_plan_sink,
            resolved_public_plan=resolved_public_plan,
            prefer_fast_public_path=prefer_fast_public_path,
        )
        public_plan = public_plan_sink.get('plan')
        deterministic_fallback_text = str(public_plan_sink.get('deterministic_text') or message_text)
    elif preview.mode is OrchestrationMode.handoff:
        handoff_payload = await rt._create_support_handoff(
            settings=settings,
            request=request,
            actor=actor,
        )
        message_text = rt._compose_handoff_answer(handoff_payload)
        deterministic_fallback_text = message_text
    elif preview.mode is OrchestrationMode.graph_rag:
        graph_rag_answer = await run_graph_rag_query(
            settings=settings,
            query=analysis_message,
        )
        if graph_rag_answer is not None:
            message_text = str(graph_rag_answer.get('text', '') or '')
        else:
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
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=4,
                visibility='public',
                category=None,
            )
            retrieval_context_pack = search.context_pack
            retrieval_hits = list(search.hits)
            citations = rt._collect_citations(retrieval_hits)
            deterministic_fallback_text = rt._compose_deterministic_answer(
                request_message=request.message,
                preview=preview,
                retrieval_hits=retrieval_hits,
                citations=citations,
                calendar_events=calendar_events,
                query_hints=query_hints,
            )
            llm_text = await compose_python_functions_with_provider(
                settings=settings,
                request_message=request.message,
                analysis_message=analysis_message,
                preview=preview,
                citations=citations,
                calendar_events=calendar_events,
                conversation_context=context_payload,
                school_profile=school_profile,
                context_pack=retrieval_context_pack,
            )
            message_text = llm_text or deterministic_fallback_text
    elif preview.mode is OrchestrationMode.hybrid_retrieval:
        used_canonical_lane = False
        restricted_document_query = (
            preview.classification.access_tier is AccessTier.authenticated
            and looks_like_restricted_document_query(request.message)
            and can_read_restricted_documents(request.user)
        )
        canonical_lane = (
            match_public_canonical_lane(analysis_message)
            if preview.classification.access_tier is AccessTier.public
            else None
        ) or (
            match_public_canonical_lane(request.message)
            if preview.classification.access_tier is AccessTier.public
            else None
        )
        if canonical_lane:
            lane_answer = compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
            if lane_answer:
                message_text = lane_answer
                deterministic_fallback_text = message_text
                used_canonical_lane = True
                preview = preview.model_copy(
                    update={
                        'reason': f'kernel_public_canonical_lane:{canonical_lane}',
                    }
                )
        if restricted_document_query:
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
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=5,
                visibility='restricted',
                category=None,
            )
            retrieval_context_pack = search.context_pack
            retrieval_hits = select_relevant_restricted_hits(analysis_message, list(search.hits))
            citations = rt._collect_citations(retrieval_hits)
            if retrieval_hits:
                message_text = compose_restricted_document_grounded_answer_for_query(
                    request.message,
                    retrieval_hits,
                ) or ''
                deterministic_fallback_text = message_text
                preview = preview.model_copy(update={'reason': 'kernel_restricted_document_search'})
            else:
                message_text = compose_restricted_document_no_match_answer(request.message)
                deterministic_fallback_text = message_text
                preview = preview.model_copy(update={'reason': 'kernel_restricted_document_no_match'})
        elif not used_canonical_lane:
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
            search = retrieval_service.hybrid_search(
                query=analysis_message,
                top_k=4,
                visibility='public',
                category=None,
            )
            retrieval_context_pack = search.context_pack
            query_hints = {
                *rt._extract_public_entity_hints(request.message),
                *rt._extract_public_entity_hints(analysis_message),
            }
            retrieval_hits = list(search.hits)
            if rt._retrieval_hits_cover_query_hints(retrieval_hits, query_hints):
                retrieval_hits = rt._filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
            citations = rt._collect_citations(retrieval_hits)
            public_answerability = rt._assess_public_answerability(
                analysis_message,
                retrieval_hits,
                query_hints,
            )
            if preview.classification.domain is QueryDomain.calendar:
                calendar_events = await rt._fetch_public_calendar(settings=settings)

            if not retrieval_hits:
                message_text = rt._compose_public_gap_answer(query_hints)
                deterministic_fallback_text = message_text
            elif not public_answerability.enough_support:
                message_text = rt._compose_answerability_gap_answer(public_answerability, request.message)
                deterministic_fallback_text = message_text
            else:
                deterministic_fallback_text = rt._compose_deterministic_answer(
                    request_message=request.message,
                    preview=preview,
                    retrieval_hits=retrieval_hits,
                    citations=citations,
                    calendar_events=calendar_events,
                    query_hints=query_hints,
                )
                llm_text = await compose_python_functions_with_provider(
                    settings=settings,
                    request_message=request.message,
                    analysis_message=analysis_message,
                    preview=preview,
                    citations=citations,
                    calendar_events=calendar_events,
                    conversation_context=context_payload,
                    school_profile=school_profile,
                    context_pack=retrieval_context_pack,
                )
                message_text = llm_text or deterministic_fallback_text
    else:
        message_text = rt._compose_deterministic_answer(
            request_message=request.message,
            preview=preview,
            retrieval_hits=retrieval_hits,
            citations=citations,
            calendar_events=calendar_events,
            query_hints=query_hints,
        )
        deterministic_fallback_text = message_text

    final_polish_decision = build_final_polish_decision(
        settings=settings,
        stack_name=effective_plan.stack_name,
        request=request,
        preview=preview,
        response_reason=preview.reason,
        llm_stages=llm_stages,
        citations_count=len(citations),
        support_count=0,
        retrieval_backend=preview.retrieval_backend,
    )
    final_polish_applied = False
    final_polish_changed_text = False
    final_polish_preserved_fallback = False

    if not (
        prefer_fast_public_path
        and preview.mode is OrchestrationMode.structured_tool
        and preview.classification.access_tier is AccessTier.public
        and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
    ) and final_polish_decision.apply_polish:
        raw_polished_text = await polish_python_functions_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=context_payload,
            school_profile=school_profile,
        )
        polished_text = rt._preserve_capability_anchor_terms(
            original_text=message_text,
            polished_text=raw_polished_text,
            request_message=request.message,
        )
        final_polish_preserved_fallback = bool(
            raw_polished_text
            and polished_text == message_text
            and rt._normalize_text(raw_polished_text) != rt._normalize_text(message_text)
        )
        if polished_text:
            llm_stages.append('structured_polish')
            final_polish_applied = True
            final_polish_changed_text = rt._normalize_text(polished_text) != rt._normalize_text(message_text)
            message_text = polished_text

    if (
        not (
            prefer_fast_public_path
            and preview.classification.access_tier is AccessTier.public
            and preview.classification.domain in {QueryDomain.institution, QueryDomain.calendar}
        )
        and final_polish_decision.run_response_critic
    ):
        revised_text = await revise_python_functions_with_provider(
            settings=settings,
            request_message=request.message,
            preview=preview,
            draft_text=message_text,
            conversation_context=context_payload,
            school_profile=school_profile,
        )
        if revised_text:
            llm_stages.append('response_critic')
            message_text = revised_text

    verifier_slot_memory = rt._build_conversation_slot_memory(
        actor=actor,
        profile=school_profile,
        conversation_context=context_payload,
        request_message=request.message,
        public_plan=public_plan,
        preview=preview,
    )
    verification, semantic_judge_used = await verify_python_functions_answer_against_contract(
        settings=settings,
        request_message=request.message,
        preview=preview,
        candidate_text=message_text,
        deterministic_fallback_text=deterministic_fallback_text,
        public_plan=public_plan,
        slot_memory=verifier_slot_memory,
    )
    if semantic_judge_used and 'answer_verifier_judge' not in llm_stages:
        llm_stages.append('answer_verifier_judge')
    if not verification.valid and deterministic_fallback_text:
        message_text = deterministic_fallback_text
        answer_verifier_fallback_used = True

    if citations:
        sources = rt._render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'
    message_text = rt._normalize_response_wording(message_text)
    message_text = _with_repair_ack(request_message=request.message, answer_text=message_text)

    visual_assets = await rt._maybe_build_visual_assets(
        settings=settings,
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=context_payload,
    )
    suggested_replies = rt._build_suggested_replies(
        request=request,
        preview=preview,
        actor=actor,
        school_profile=school_profile,
        conversation_context=context_payload,
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
        conversation_context=context_payload,
        public_plan=public_plan,
        request_message=request.message,
        message_text=message_text,
        citations_count=len(citations),
        suggested_reply_count=len(suggested_replies),
        visual_asset_count=len(visual_assets),
        answer_verifier_valid=verification.valid,
        answer_verifier_reason=verification.reason,
        answer_verifier_fallback_used=answer_verifier_fallback_used,
        deterministic_fallback_available=bool(deterministic_fallback_text),
        answer_verifier_judge_used=semantic_judge_used,
        langgraph_trace_metadata={},
    )

    selected_tools = list(preview.selected_tools)
    if (
        preview.mode is OrchestrationMode.structured_tool
        and preview.classification.domain is QueryDomain.institution
        and preview.classification.access_tier is AccessTier.public
        and 'get_public_school_profile' not in selected_tools
    ):
        selected_tools = [*selected_tools, 'get_public_school_profile']

    response = MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=preview.retrieval_backend,
        selected_tools=selected_tools,
        citations=citations,
        visual_assets=visual_assets,
        suggested_replies=suggested_replies,
        calendar_events=calendar_events,
        evidence_pack=_build_kernel_evidence_pack(
            request=request,
            plan=effective_plan,
            preview=preview,
            selected_tools=selected_tools,
            citations=citations,
            school_profile=school_profile,
            has_known_unknown_answer=bool(unpublished_public_answer),
        ),
        needs_authentication=preview.needs_authentication,
        graph_path=[*preview.graph_path, f'kernel:{effective_plan.stack_name}'],
        risk_flags=[
            *preview.risk_flags,
            *(["valid_but_unpublished"] if unpublished_public_answer and "valid_but_unpublished" not in preview.risk_flags else []),
        ],
        reason=preview.reason,
        used_llm=bool(llm_stages),
        llm_stages=list(dict.fromkeys(llm_stages)),
        final_polish_eligible=final_polish_decision.eligible,
        final_polish_applied=final_polish_applied,
        final_polish_mode=final_polish_decision.mode,
        final_polish_reason=final_polish_decision.reason,
        final_polish_changed_text=final_polish_changed_text,
        final_polish_preserved_fallback=final_polish_preserved_fallback,
    )
    reflection = KernelReflection(
        grounded=verification.valid,
        verifier_reason=verification.reason,
        fallback_used=answer_verifier_fallback_used,
        answer_judge_used=semantic_judge_used,
        notes=[
            f'route:{preview.mode.value}',
            f'slice:{effective_plan.slice_name}',
            *effective_plan.plan_notes,
        ],
    )
    return KernelRunResult(
        plan=effective_plan,
        reflection=reflection,
        response=response.model_dump(mode='json'),
    )
