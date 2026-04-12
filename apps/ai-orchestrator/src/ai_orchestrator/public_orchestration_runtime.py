from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Public routing and orchestration helpers extracted from runtime_core.py."""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import (
    _recent_conversation_focus,
    _recent_message_lines,
    _recent_trace_focus,
    _recent_workflow_focus,
)
from .public_act_rules_runtime import _matched_public_act_rules, _prioritize_public_act_rules


LOCAL_EXTRACTED_NAMES = {
    '_intent_analysis_impl',
    '_looks_like_family_admin_aggregate_query',
}


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


def _refresh_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _looks_like_family_admin_aggregate_query(message: str) -> bool:
    return _intent_analysis_impl('_looks_like_family_admin_aggregate_query')(message)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _normalize_text(text: str) -> str:
    return _intent_analysis_impl('_normalize_text')(text)


def _looks_like_workflow_resume_follow_up(message: str) -> bool:
    from .analysis_context_runtime import _looks_like_workflow_resume_follow_up as _impl

    return _impl(message)


def _detect_visit_booking_action(message: str) -> str | None:
    from .workflow_runtime import _detect_visit_booking_action as _impl

    return _impl(message)


def _looks_like_visit_update_follow_up(message: str) -> bool:
    from .analysis_context_runtime import _looks_like_visit_update_follow_up as _impl

    return _impl(message)


def _detect_institutional_request_action(message: str) -> str | None:
    from .workflow_runtime import _detect_institutional_request_action as _impl

    return _impl(message)


def _extract_school_reference_candidate(message: str) -> str | None:
    normalized = _normalize_text(message)
    stop_tokens = {
        'proximo',
        'próximo',
        'passo',
        'regularizar',
        'retrato',
        'panorama',
        'quadro',
        'pendencia',
        'pendencias',
        'pendência',
        'pendências',
        'situacao',
        'situação',
        'resumo',
        'setor',
        'departamento',
        'area',
        'área',
        'fila',
        'na',
        'no',
        'em',
        'quinta',
        'sexta',
        'segunda',
        'terca',
        'terça',
        'quarta',
        'sabado',
        'sábado',
        'domingo',
        'manha',
        'manhã',
        'tarde',
        'noite',
        'diretor',
        'diretora',
        'secretaria',
        'secretariao',
        'humano',
        'atendimento',
        'financeiro',
        'matricula',
        'matrícula',
        'coordenacao',
        'coordenação',
        'orientacao',
        'orientação',
        'professor',
        'professora',
        'oferece',
        'tem',
        'fica',
        'abre',
        'fecha',
        'aceita',
        'publica',
        'publico',
        'funciona',
        'site',
        'instagram',
        'telefone',
        'whatsapp',
        'email',
        'descreve',
        'explica',
        'explique',
        'mostra',
        'mostre',
        'quais',
        'qual',
        'que',
        'como',
        'onde',
        'quando',
        'para',
        'pra',
        'mecanismos',
        'publicos',
        'públicos',
    }
    generic_phrase_tokens = {
        'proximo',
        'próximo',
        'passo',
        'regularizar',
        'pendencia',
        'pendencias',
        'pendência',
        'pendências',
        'situacao',
        'situação',
        'resumo',
        'retrato',
        'panorama',
        'quadro',
    }
    patterns = (
        r'\b(?:colegio|colégio)\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\b(?:e|é)\s+do\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\b(?:nao|não)\s+e\s+do\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
        r'\bfalar com\s+(?:o|a)\s+([a-z0-9]+(?:\s+[a-z0-9]+){0,3})\b',
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        candidate = match.group(1).strip()
        candidate_tokens = [
            token for token in candidate.split() if token not in {'o', 'a', 'do', 'da', 'de'}
        ]
        if not candidate_tokens:
            continue
        if candidate_tokens[0] in stop_tokens:
            continue
        if set(candidate_tokens) & generic_phrase_tokens:
            continue
        if len(candidate_tokens) == 1 and candidate_tokens[0] in stop_tokens:
            continue
        return ' '.join(candidate_tokens)
    return None


def _school_identity_tokens(profile: dict[str, Any] | None) -> set[str]:
    school_name = _normalize_text(str((profile or {}).get('school_name', '') or ''))
    return {
        token
        for token in school_name.split()
        if token and token not in {'colegio', 'colégio', 'escola', 'do', 'da', 'de'}
    }


def _foreign_school_reference(
    *,
    message: str,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _is_public_teacher_identity_query(message):
        return None
    if _is_comparative_query(message):
        return None
    normalized = _normalize_text(message)
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
    recent_student_name = str(
        recent_focus.get('academic_student_name')
        or recent_focus.get('finance_student_name')
        or recent_focus.get('student_name')
        or ''
    ).strip()
    school_tokens = _school_identity_tokens(school_profile)
    direct_reference = _extract_school_reference_candidate(message)
    if direct_reference:
        direct_reference_tokens = set(direct_reference.split())
        support_like_tokens = {
            'setor',
            'financeiro',
            'secretaria',
            'direcao',
            'direção',
            'diretoria',
            'coordenacao',
            'coordenação',
            'matricula',
            'matrícula',
            'atendimento',
            'humano',
            'fila',
        }
        if direct_reference_tokens & support_like_tokens:
            return None
        if (
            normalized.startswith('e do ')
            or normalized.startswith('e da ')
            or normalized.startswith('do ')
            or normalized.startswith('da ')
        ) and (
            recent_active_task.startswith(('academic:', 'finance:', 'admin:'))
            or bool(recent_student_name)
        ):
            return None
        reference_tokens = set(direct_reference.split())
        if not (reference_tokens & school_tokens):
            return direct_reference
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'falar com',
            'me passa',
            'passa pro',
            'passa para',
            'diretor',
            'diretora',
            'contato',
        }
    ):
        return None
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        historical_reference = _extract_school_reference_candidate(content)
        if not historical_reference:
            continue
        reference_tokens = set(historical_reference.split())
        if reference_tokens & school_tokens:
            continue
        return historical_reference
    return None


def _compose_foreign_school_redirect(
    *,
    school_profile: dict[str, Any] | None,
    foreign_school_reference: str,
) -> str:
    school_name = str((school_profile or {}).get('school_name', '') or 'Colégio Horizonte').strip()
    foreign_school_name = foreign_school_reference.title()
    return (
        f'Aqui e o {school_name}. Se voce esta procurando o {foreign_school_name}, '
        'eu nao tenho acesso ao atendimento dessa outra instituicao. '
        f'Se quiser, sigo te ajudando com o {school_name} por aqui.'
    )


def _extract_term_filter(message: str) -> str | None:
    lowered = _normalize_text(message)
    patterns = {
        'B1': [r'\bb1\b', r'\b1o?\s*bimestre\b', r'\bprimeiro\s*bimestre\b'],
        'B2': [r'\bb2\b', r'\b2o?\s*bimestre\b', r'\bsegundo\s*bimestre\b'],
        'B3': [r'\bb3\b', r'\b3o?\s*bimestre\b', r'\bterceiro\s*bimestre\b'],
        'B4': [r'\bb4\b', r'\b4o?\s*bimestre\b', r'\bquarto\s*bimestre\b'],
    }
    for suffix, candidates in patterns.items():
        if any(re.search(candidate, lowered) for candidate in candidates):
            return suffix
    return None


def _user_role_from_actor(actor: dict[str, Any] | None) -> UserRole:
    role_code = actor.get('role_code') if isinstance(actor, dict) else None
    if isinstance(role_code, str):
        try:
            return UserRole(role_code)
        except ValueError:
            return UserRole.anonymous
    return UserRole.anonymous


def _user_context_from_actor(actor: dict[str, Any] | None) -> UserContext:
    if not actor:
        return UserContext()

    linked_student_ids = actor.get('linked_student_ids')
    if not isinstance(linked_student_ids, list):
        linked_student_ids = []

    return UserContext(
        role=_user_role_from_actor(actor),
        authenticated=True,
        linked_student_ids=[str(student_id) for student_id in linked_student_ids],
        scopes=[],
    )


def _merge_user_context(actor: dict[str, Any] | None, request_user: UserContext) -> UserContext:
    actor_user = _user_context_from_actor(actor)
    if actor is None:
        return request_user
    linked_student_ids: list[str] = []
    seen_students: set[str] = set()
    for student_id in [*actor_user.linked_student_ids, *request_user.linked_student_ids]:
        normalized = str(student_id or '').strip()
        if not normalized or normalized in seen_students:
            continue
        seen_students.add(normalized)
        linked_student_ids.append(normalized)
    scopes: list[str] = []
    seen_scopes: set[str] = set()
    for scope in [*actor_user.scopes, *request_user.scopes]:
        normalized = str(scope or '').strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen_scopes:
            continue
        seen_scopes.add(key)
        scopes.append(normalized)
    role = actor_user.role if actor_user.role is not UserRole.anonymous else request_user.role
    return UserContext(
        role=role,
        authenticated=actor_user.authenticated or request_user.authenticated,
        linked_student_ids=linked_student_ids,
        scopes=scopes,
    )


def _should_run_public_semantic_resolver(
    *,
    message: str,
    preview: Any,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    if preview.classification.access_tier is not AccessTier.public:
        return False
    if preview.mode not in {
        OrchestrationMode.structured_tool,
        OrchestrationMode.hybrid_retrieval,
        OrchestrationMode.clarify,
    }:
        return False
    matched_rules = _prioritize_public_act_rules(
        message,
        _matched_public_act_rules(message, conversation_context=conversation_context),
    )
    if not _has_public_multi_intent_signal(message) and matched_rules:
        primary_rule = matched_rules[0]
        if primary_rule.name in {
            'greeting',
            'utility_date',
            'auth_guidance',
            'access_scope',
            'language_preference',
            'scope_boundary',
            'assistant_identity',
            'service_routing',
            'capabilities',
            'document_submission',
            'careers',
            'teacher_directory',
            'leadership',
            'web_presence',
            'social_presence',
            'contacts',
            'operating_hours',
            'timeline',
            'calendar_events',
            'location',
            'pricing',
            'schedule',
            'features',
            'segments',
            'school_name',
        }:
            return False
    return True


def _is_public_semantic_rescue_candidate(preview: Any) -> bool:
    if preview.classification.domain not in {QueryDomain.institution, QueryDomain.calendar}:
        return False
    if preview.classification.access_tier is not AccessTier.public:
        return False
    return preview.mode in {OrchestrationMode.hybrid_retrieval, OrchestrationMode.clarify}


def _should_apply_public_semantic_rescue(
    *,
    preview: Any,
    plan: PublicInstitutionPlan | None,
) -> bool:
    if plan is None:
        return False
    if plan.semantic_source != 'llm':
        return False
    if plan.conversation_act not in PUBLIC_SEMANTIC_RESCUE_ACTS:
        return False
    if preview.mode is OrchestrationMode.clarify:
        return True
    if preview.mode is OrchestrationMode.hybrid_retrieval:
        return True
    return False


def _recent_student_disambiguation_domain(
    conversation_context: dict[str, Any] | None,
) -> QueryDomain | None:
    if not isinstance(conversation_context, dict):
        return None
    recent_assistant = _extract_recent_assistant_message(
        conversation_context.get('recent_messages', [])
    )
    if 'mais de um aluno vinculado' not in _normalize_text(recent_assistant or ''):
        return None
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if not isinstance(recent_focus, dict):
        return None
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    if active_task.startswith('academic:'):
        return QueryDomain.academic
    if active_task.startswith('finance:'):
        return QueryDomain.finance
    return None


def _protected_selected_tools_for_domain(domain: QueryDomain) -> list[str]:
    if domain is QueryDomain.academic:
        return [
            'get_student_academic_summary',
            'get_student_attendance',
            'get_student_grades',
            'get_student_upcoming_assessments',
            'get_student_attendance_timeline',
        ]
    if domain is QueryDomain.institution:
        return [
            'get_administrative_status',
            'get_student_administrative_status',
        ]
    return ['get_financial_summary']


def _apply_protected_domain_override(
    preview: Any,
    *,
    domain: QueryDomain,
    confidence: float,
    reason: str,
    graph_marker: str,
) -> None:
    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=domain,
        access_tier=AccessTier.sensitive
        if domain is QueryDomain.finance
        else AccessTier.authenticated,
        confidence=confidence,
        reason=reason,
    )
    preview.selected_tools = _protected_selected_tools_for_domain(domain)
    if domain is QueryDomain.academic:
        preview.output_contract = 'dados academicos autorizados, auditaveis e minimizados'
        preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    elif domain is QueryDomain.finance:
        preview.output_contract = 'dados financeiros autorizados, auditaveis e com trilha reforcada'
        if 'sensitive_data_path' not in preview.risk_flags:
            preview.risk_flags = [*preview.risk_flags, 'sensitive_data_path']
    else:
        preview.output_contract = 'dados administrativos autorizados, auditaveis e minimizados'
        preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = reason
    preview.graph_path = [*preview.graph_path, graph_marker]


def _explicit_protected_domain_hint(
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    conversation_context: dict[str, Any] | None = None,
) -> QueryDomain | None:
    _refresh_runtime_core_namespace()
    normalized = _normalize_text(message)
    if _looks_like_family_admin_aggregate_query(message):
        return QueryDomain.institution
    if _looks_like_family_finance_aggregate_query(message):
        return QueryDomain.finance
    if _looks_like_family_attendance_aggregate_query(message):
        return QueryDomain.academic
    if _looks_like_family_academic_aggregate_query(message):
        return QueryDomain.academic
    linked_students = _linked_students(actor)
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_slot_memory = _recent_trace_slot_memory(conversation_context) or {}
    recent_focus_kind = str(recent_focus.get('kind') or recent_slot_memory.get('kind') or '')
    recent_active_task = str(
        recent_focus.get('active_task') or recent_slot_memory.get('active_task') or ''
    )
    protected_academic_subject_follow_up = recent_active_task.startswith('academic:') and (
        (
            _is_follow_up_query(message)
            and (
                _requested_subject_label_from_message(message) is not None
                or _extract_unknown_subject_reference(message) is not None
            )
        )
        or _wants_missing_subject_explanation_follow_up(
            message,
            conversation_context=conversation_context,
        )
    )
    if protected_academic_subject_follow_up:
        return QueryDomain.academic
    if _message_has_public_followup_signal(message, conversation_context=conversation_context):
        return None
    if _detect_public_pricing_price_kind(message) is not None and (
        resolve_entity_hints(message).quantity_hint is not None
        or _select_public_segment(message) is not None
        or _extract_public_pricing_grade_year(message) is not None
        or any(
            _message_matches_term(normalized, term)
            for term in {'filho', 'filha', 'filhos', 'filhas', 'aluno', 'alunos'}
        )
        or _is_public_pricing_context_follow_up(message, conversation_context=conversation_context)
    ):
        return None
    if looks_like_restricted_document_query(message):
        return None
    if match_public_canonical_lane(message):
        return None
    if (
        _is_service_routing_query(message)
        or _matches_public_contact_rule(message)
        or _matches_public_location_rule(message)
        or _is_auth_guidance_query(message)
        or _is_access_scope_query(message)
        or _is_public_document_submission_query(message)
        or _is_public_timeline_query(message)
        or _is_public_calendar_event_query(message)
        or _is_public_policy_query(message)
        or _is_public_pricing_navigation_query(message)
        or _is_public_pricing_context_follow_up(message, conversation_context=conversation_context)
        or _is_public_curriculum_query(message)
        or _is_public_curriculum_context_follow_up(
            message, conversation_context=conversation_context
        )
        or _is_public_capacity_query(message)
        or _matches_public_highlight_rule(message)
    ):
        return None
    academic_risk_follow_up = any(
        _message_matches_term(normalized, term)
        for term in {
            'risco academico',
            'risco acadêmico',
            'maior risco',
            'pontos de maior risco',
            'pontos academicos que mais preocupam',
            'pontos acadêmicos que mais preocupam',
            'pontos academicos',
            'pontos acadêmicos',
            'pontos mais sensiveis',
            'pontos mais sensíveis',
            'mais preocupam',
            'mais perto do limite',
            'mais perto da media',
            'mais perto da média',
            'mais proximo do limite',
            'mais próximo do limite',
            'mais vulneravel',
            'mais vulnerável',
            'preocupacao academica',
            'preocupação acadêmica',
            'preocupacoes academicas',
            'preocupações acadêmicas',
        }
    )
    academic_difficulty_follow_up = _looks_like_academic_difficulty_query(
        message,
        conversation_context=conversation_context,
    )
    if (
        _detect_academic_attribute_request(message) is not None
        or _detect_academic_focus_kind(message) is not None
    ):
        return QueryDomain.academic
    if academic_difficulty_follow_up:
        return QueryDomain.academic
    if (
        _detect_finance_attribute_request(message) is not None
        or _detect_finance_status_filter(message) is not None
        or any(
            _message_matches_term(_normalize_text(message), term)
            for term in FINANCE_SECOND_COPY_TERMS
        )
    ):
        return QueryDomain.finance
    if not isinstance(actor, dict):
        return None
    if not linked_students:
        return None
    mentions_linked_student = bool(
        _matching_students_in_text(linked_students, message)
        or _student_focus_candidate(actor, message)
    )
    protected_follow_up = _is_follow_up_query(message) and bool(recent_focus)
    if mentions_linked_student and protected_follow_up:
        if recent_active_task.startswith('academic:'):
            return QueryDomain.academic
        if recent_active_task.startswith('finance:'):
            return QueryDomain.finance
        if recent_active_task.startswith('admin:'):
            return QueryDomain.institution
    requested_subject_label = _requested_subject_label_from_message(message)
    if (
        requested_subject_label
        and _looks_like_subject_existence_query(message)
        and (
            mentions_linked_student
            or protected_follow_up
            or recent_focus_kind == 'academic'
            or recent_active_task.startswith('academic:')
        )
    ):
        return QueryDomain.academic
    if any(_message_matches_term(normalized, term) for term in PERSONAL_ADMIN_STATUS_TERMS) and (
        mentions_linked_student
        or protected_follow_up
        or recent_focus_kind in {'academic', 'finance', 'secretaria'}
        or recent_active_task.startswith(('admin:', 'academic:', 'finance:'))
    ):
        return QueryDomain.institution
    if academic_risk_follow_up and (
        mentions_linked_student
        or protected_follow_up
        or recent_focus_kind == 'academic'
        or recent_active_task.startswith('academic:')
    ):
        return QueryDomain.academic
    if (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'financeiro',
                'mensalidade',
                'mensalidades',
                'boleto',
                'boletos',
                'fatura',
                'faturas',
                'pagamento',
                'pagamentos',
                'contrato',
            }
        )
        and not _is_public_pricing_navigation_query(message)
        and (
            mentions_linked_student
            or protected_follow_up
            or recent_focus_kind in {'academic', 'finance'}
        )
    ):
        return QueryDomain.finance
    return None


def _apply_protected_domain_rescue(
    *,
    preview: Any,
    actor: dict[str, Any] | None,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    current_domain = getattr(getattr(preview, 'classification', None), 'domain', None)
    if current_domain not in {
        QueryDomain.unknown,
        QueryDomain.institution,
        QueryDomain.academic,
        QueryDomain.finance,
    }:
        return False
    target_domain = _explicit_protected_domain_hint(
        message,
        actor=actor,
        conversation_context=conversation_context,
    )
    if target_domain is None:
        return False
    selected_tools = set(getattr(preview, 'selected_tools', []) or [])
    needs_retool = not set(_protected_selected_tools_for_domain(target_domain)).issubset(
        selected_tools
    )
    if (
        target_domain is current_domain
        and preview.mode is OrchestrationMode.structured_tool
        and not needs_retool
    ):
        return False
    _apply_protected_domain_override(
        preview,
        domain=target_domain,
        confidence=0.89,
        reason='o turno atual trouxe pistas explicitas de outro dominio protegido e o roteamento foi corrigido',
        graph_marker='protected_domain_rescue',
    )
    return True


def _is_public_support_navigation_query(message: str) -> bool:
    normalized = _normalize_text(message)
    explicit_handoff_terms = {
        'quero falar com um atendente humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'me transfira',
        'me encaminhe',
        'abra um protocolo',
        'abrir protocolo',
        'quero abrir um chamado',
        'quero registrar um caso',
    }
    if any(_message_matches_term(normalized, term) for term in explicit_handoff_terms):
        return False
    if _looks_like_public_explanatory_bundle_query(message):
        return False
    return any(
        matcher(message)
        for matcher in (
            _is_service_routing_query,
            _matches_public_contact_rule,
            _matches_public_location_rule,
            _is_public_timeline_query,
            _is_public_calendar_event_query,
            _is_public_navigation_query,
            _is_public_policy_query,
            _matches_public_highlight_rule,
        )
    )


def _looks_like_public_explanatory_bundle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if match_public_canonical_lane(message):
        return True
    explanatory_terms = {
        'como',
        'quais evidencias',
        'que evidencias',
        'quero entender',
        'quero uma leitura ampla',
        'como se completam',
        'como aparecem combinados',
        'como o material publico liga',
        'como a escola costura',
        'como a familia sai',
        'como frequência',
        'como frequencia',
    }
    topic_terms = {
        'inclus',
        'acessib',
        'integral',
        'estudo orientado',
        'medic',
        'emerg',
        'saida',
        'autoriz',
        'transporte',
        'uniforme',
        'alimenta',
        'direcao',
        'direção',
        'coordenacao',
        'coordenação',
        'pontualidade',
        'convivencia',
        'convivência',
        'frequencia',
        'frequência',
    }
    topic_count = sum(1 for term in topic_terms if term in normalized)
    return topic_count >= 2 and any(term in normalized for term in explanatory_terms)


def _looks_like_public_documentary_open_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if match_public_canonical_lane(message):
        return True
    documentary_verbs = {
        'quero entender',
        'me explique',
        'explique',
        'como a escola',
        'como a familia',
        'como a família',
        'como isso se organiza',
        'como isso se conecta',
        'como isso se articula',
        'qual imagem institucional',
        'qual a imagem institucional',
        'que leitura ampla',
        'que leitura integrada',
        'quais evidencias',
        'quais evidências',
        'que evidencias',
        'que evidências',
    }
    documentary_topics = {
        'inclus',
        'acessib',
        'seguran',
        'apoio',
        'estudo orientado',
        'turno estendido',
        'contraturno',
        'saude',
        'saúde',
        'emerg',
        'avali',
        'saida',
        'saída',
        'autoriz',
        'atividade externa',
        'transporte',
        'uniforme',
        'alimenta',
        'cantina',
        'refeicao',
        'refeição',
        'deslocamento',
        'identificacao',
        'identificação',
        'governan',
        'protocolo',
        'lideranca',
        'liderança',
        'coordenacao',
        'coordenação',
        'direcao',
        'direção',
        'responsaveis',
        'responsáveis',
        'devolut',
        'recompos',
        'atendimento digital',
        'encaminhamento',
    }
    topic_hits = sum(1 for term in documentary_topics if term in normalized)
    return topic_hits >= 2 and any(term in normalized for term in documentary_verbs)


def _public_open_documentary_topic(message: str) -> str | None:
    normalized = _normalize_text(message)
    if not _looks_like_public_documentary_open_query(message):
        return None
    extended_day_hits = sum(
        1
        for term in (
            'turno estendido',
            'contraturno',
            'oficinas',
            'refeicao',
            'refeição',
            'estudo guiado',
            'estudo acompanhado',
            'permanencia',
            'permanência',
        )
        if term in normalized
    )
    if extended_day_hits >= 3:
        return 'extended_day_ecosystem'
    governance_hits = sum(
        1
        for term in (
            'secretaria',
            'coordenacao',
            'coordenação',
            'direcao',
            'direção',
            'canais oficiais',
            'trilha institucional',
            'escalonamento',
            'tema caminha',
        )
        if term in normalized
    )
    if governance_hits >= 3:
        return 'governance_channels'
    health_hits = sum(
        1
        for term in (
            'saude',
            'saúde',
            'atestado',
            'comprovacao',
            'comprovação',
            'atividade avaliativa',
            'avaliativa',
            'ausencia',
            'ausência',
            'reorganizacao',
            'reorganização',
            'pedagogica',
            'pedagógica',
        )
        if term in normalized
    )
    if health_hits >= 3:
        return 'health_reorganization'
    return None


def _public_open_documentary_secondary_acts(topic: str) -> tuple[str, ...]:
    if topic == 'extended_day_ecosystem':
        return ('features', 'schedule')
    if topic == 'governance_channels':
        return ('contacts', 'leadership')
    if topic == 'health_reorganization':
        return ('policy', 'timeline')
    return ()


def _public_open_documentary_tools(topic: str) -> tuple[str, ...]:
    if topic == 'extended_day_ecosystem':
        return ('get_public_school_profile',)
    if topic == 'governance_channels':
        return ('get_public_school_profile', 'get_org_directory', 'get_service_directory')
    if topic == 'health_reorganization':
        return ('get_public_school_profile', 'get_public_timeline')
    return ('get_public_school_profile',)


def _apply_public_open_documentary_plan(
    message: str,
    plan: PublicInstitutionPlan,
) -> PublicInstitutionPlan:
    topic = _public_open_documentary_topic(message)
    if topic is None:
        return plan
    existing_secondary = tuple(
        act
        for act in plan.secondary_acts
        if act not in {'comparative', 'highlight', 'features', 'curriculum'}
        or act in _public_open_documentary_secondary_acts(topic)
    )
    merged_secondary = tuple(
        dict.fromkeys([*_public_open_documentary_secondary_acts(topic), *existing_secondary])
    )[:2]
    required_tools = tuple(
        dict.fromkeys([*plan.required_tools, *_public_open_documentary_tools(topic)])
    )
    return replace(
        plan,
        conversation_act='canonical_fact',
        secondary_acts=merged_secondary,
        required_tools=required_tools,
        fetch_profile=True,
        focus_hint=topic,
        semantic_source='open_documentary_rules',
    )


def _should_use_public_open_documentary_synthesis(
    message: str,
    plan: PublicInstitutionPlan | None,
) -> bool:
    if plan is None:
        return False
    if _public_open_documentary_topic(message) is None:
        return False
    return plan.semantic_source in {'open_documentary_rules', 'llm'}


def _apply_public_support_rescue(
    *,
    preview: Any,
    message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> bool:
    if getattr(getattr(preview, 'classification', None), 'domain', None) is not QueryDomain.support:
        return False
    if preview.mode not in {
        OrchestrationMode.handoff,
        OrchestrationMode.structured_tool,
        OrchestrationMode.clarify,
    }:
        return False
    if not _is_public_support_navigation_query(message):
        return False
    plan = _build_public_institution_plan(
        message,
        [],
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=QueryDomain.institution,
        access_tier=AccessTier.public,
        confidence=0.9,
        reason='consulta publica de navegacao e canais foi resgatada do dominio support',
    )
    preview.selected_tools = list(plan.required_tools)
    preview.output_contract = (
        'roteamento publico da escola, com canais, contatos e fatos institucionais auditaveis'
    )
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = 'public_support_rescue'
    preview.graph_path = [*preview.graph_path, 'public_support_rescue']
    preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    return True


def _apply_authenticated_public_profile_rescue(
    *,
    preview: Any,
    actor: dict[str, Any] | None,
    message: str,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> bool:
    if preview.classification.access_tier is AccessTier.public:
        return False
    if preview.mode not in {
        OrchestrationMode.structured_tool,
        OrchestrationMode.hybrid_retrieval,
        OrchestrationMode.clarify,
    }:
        return False
    explicit_public_signal = (
        _is_public_pricing_navigation_query(message)
        or _is_public_pricing_context_follow_up(message, conversation_context=conversation_context)
        or _is_public_curriculum_query(message)
        or _is_public_curriculum_context_follow_up(
            message, conversation_context=conversation_context
        )
    )
    if not explicit_public_signal:
        return False
    if _should_prioritize_protected_sql_query(
        message,
        actor=actor,
        conversation_context=conversation_context,
    ):
        return False
    plan = _build_public_institution_plan(
        message,
        [],
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=QueryDomain.institution,
        access_tier=AccessTier.public,
        confidence=0.91,
        reason='consulta publica institucional foi resgatada antes de cair em trilho protegido',
    )
    preview.selected_tools = list(plan.required_tools)
    preview.output_contract = 'fatos publicos institucionais da escola, com foco em curriculo, oferta e precificacao publicada'
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = 'authenticated_public_profile_rescue'
    preview.graph_path = [*preview.graph_path, 'authenticated_public_profile_rescue']
    preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    return True


def _apply_workflow_follow_up_rescue(
    *,
    preview: Any,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    recent_focus = _recent_workflow_focus(conversation_context)
    if recent_focus is None:
        recent_focus = _recent_trace_focus(conversation_context) or _recent_conversation_focus(
            conversation_context
        )
    if not isinstance(recent_focus, dict):
        return False
    focus_kind = str(recent_focus.get('kind', '') or '').strip()
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    if focus_kind not in {'visit', 'request', 'support'} and not active_task.startswith(
        'workflow:'
    ):
        return False

    normalized = _normalize_text(message)
    selected_tools: list[str] | None = None
    reason = ''
    graph_marker = 'workflow_follow_up_rescue'

    if focus_kind == 'visit' or active_task == 'workflow:visit_booking':
        visit_action = _detect_visit_booking_action(message)
        if visit_action is not None or _looks_like_visit_update_follow_up(message):
            selected_tools = ['update_visit_booking']
            reason = 'workflow_follow_up_rescue:visit_update'
            graph_marker = 'workflow_follow_up_rescue_visit_update'
        elif (
            'protocolo' in normalized
            or any(_message_matches_term(normalized, term) for term in WORKFLOW_STATUS_TERMS)
            or _looks_like_workflow_resume_follow_up(message)
            or any(
                phrase in normalized
                for phrase in {
                    'resume',
                    'resuma',
                    'qual o protocolo',
                    'qual e o protocolo',
                    'qual é o protocolo',
                }
            )
        ):
            selected_tools = ['get_workflow_status']
            if _looks_like_workflow_resume_follow_up(message):
                reason = 'workflow_follow_up_rescue:visit_resume'
                graph_marker = 'workflow_follow_up_rescue_visit_resume'
            else:
                reason = 'workflow_follow_up_rescue:visit_status'
                graph_marker = 'workflow_follow_up_rescue_visit_status'
    elif focus_kind == 'request' or active_task == 'workflow:institutional_request':
        request_action = _detect_institutional_request_action(message)
        if request_action is not None:
            selected_tools = ['update_institutional_request']
            reason = 'workflow_follow_up_rescue:request_update'
            graph_marker = 'workflow_follow_up_rescue_request_update'
        elif (
            'protocolo' in normalized
            or any(_message_matches_term(normalized, term) for term in WORKFLOW_STATUS_TERMS)
            or any(
                phrase in normalized
                for phrase in {
                    'resume',
                    'resuma',
                    'qual o protocolo',
                    'qual e o protocolo',
                    'qual é o protocolo',
                }
            )
        ):
            selected_tools = ['get_workflow_status']
            reason = 'workflow_follow_up_rescue:request_status'
            graph_marker = 'workflow_follow_up_rescue_request_status'
    elif focus_kind == 'support' or active_task == 'workflow:human_handoff':
        if (
            'protocolo' in normalized
            or any(_message_matches_term(normalized, term) for term in WORKFLOW_STATUS_TERMS)
            or any(
                phrase in normalized
                for phrase in {
                    'resume',
                    'resuma',
                    'qual o protocolo',
                    'qual e o protocolo',
                    'qual é o protocolo',
                }
            )
        ):
            selected_tools = ['get_workflow_status']
            reason = 'workflow_follow_up_rescue:support_status'
            graph_marker = 'workflow_follow_up_rescue_support_status'

    if not selected_tools:
        return False

    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=QueryDomain.support,
        access_tier=AccessTier.public,
        confidence=0.93,
        reason='turno atual e um follow-up operacional de workflow e deve continuar no protocolo ativo',
    )
    preview.selected_tools = selected_tools
    preview.output_contract = 'workflow follow-up com protocolo, status, remarcacao ou cancelamento usando o contexto operacional recente'
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = reason
    preview.graph_path = [*preview.graph_path, graph_marker]
    preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    return True


def _apply_teacher_role_rescue(
    *,
    preview: Any,
    actor: dict[str, Any] | None,
    user: UserContext | None,
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    user_role = user.role.value if isinstance(user, UserContext) else ''
    if actor_role != 'teacher' and not (
        isinstance(user, UserContext) and user.authenticated and user_role == UserRole.teacher.value
    ):
        return False
    if not _is_teacher_scope_guidance_query(
        message,
        actor=actor,
        user=user,
        conversation_context=conversation_context,
    ):
        return False

    preview.mode = OrchestrationMode.structured_tool
    preview.classification = IntentClassification(
        domain=QueryDomain.academic,
        access_tier=AccessTier.authenticated,
        confidence=0.94 if actor_role == 'teacher' else 0.9,
        reason=(
            'mensagem indica autoatendimento docente e a conta atual tem perfil de professor'
            if actor_role == 'teacher'
            else 'mensagem indica autoatendimento docente e a sessao autenticada informa perfil de professor'
        ),
    )
    preview.selected_tools = ['get_teacher_schedule']
    preview.output_contract = 'grade docente e autoatendimento permitido ao professor'
    preview.retrieval_backend = RetrievalBackend.none
    preview.citations_required = False
    preview.needs_authentication = False
    preview.reason = 'teacher_role_rescue'
    preview.graph_path = [*preview.graph_path, 'teacher_role_rescue']
    preview.risk_flags = [flag for flag in preview.risk_flags if flag != 'sensitive_data_path']
    return True


def _apply_student_disambiguation_rescue(
    *,
    preview: Any,
    actor: dict[str, Any] | None,
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if preview.mode is not OrchestrationMode.clarify:
        return False
    if not isinstance(actor, dict):
        return False
    rescued_domain = _recent_student_disambiguation_domain(conversation_context)
    if rescued_domain is None:
        return False
    capability = 'finance' if rescued_domain is QueryDomain.finance else 'academic'
    matched_students = _matching_students_in_text(
        _eligible_students(actor, capability=capability),
        message,
    )
    if len(matched_students) != 1:
        return False

    _apply_protected_domain_override(
        preview,
        domain=rescued_domain,
        confidence=0.87,
        reason='o usuario respondeu a desambiguacao do aluno e o fluxo protegido pode continuar',
        graph_marker='student_disambiguation_rescue',
    )
    return True


def _normalize_public_semantic_plan(payload: dict[str, Any] | None) -> PublicInstitutionPlan | None:
    if not isinstance(payload, dict):
        return None
    conversation_act = str(payload.get('conversation_act', '')).strip()
    if conversation_act not in PUBLIC_SEMANTIC_ACTS:
        return None
    required_tools_raw = payload.get('required_tools', [])
    required_tools = (
        tuple(
            tool_name
            for tool_name in required_tools_raw
            if isinstance(tool_name, str) and tool_name in PUBLIC_SEMANTIC_TOOLS
        )
        if isinstance(required_tools_raw, list)
        else ()
    )
    secondary_acts_raw = payload.get('secondary_acts', [])
    secondary_acts = (
        tuple(
            act
            for act in secondary_acts_raw
            if isinstance(act, str) and act in PUBLIC_SEMANTIC_ACTS and act != conversation_act
        )
        if isinstance(secondary_acts_raw, list)
        else ()
    )
    requested_attribute = str(payload.get('requested_attribute', '')).strip() or None
    if requested_attribute == 'none':
        requested_attribute = None
    requested_channel = str(payload.get('requested_channel', '')).strip() or None
    if requested_channel == 'none':
        requested_channel = None
    focus_hint = str(payload.get('focus_hint', '')).strip() or None
    fetch_profile = 'get_public_school_profile' in required_tools or conversation_act in {
        'web_presence',
        'social_presence',
        'comparative',
        'pricing',
        'schedule',
        'operating_hours',
        'curriculum',
        'features',
        'highlight',
        'visit',
        'location',
        'confessional',
        'kpi',
        'document_submission',
        'careers',
        'teacher_directory',
        'segments',
        'school_name',
        'calendar_events',
        'canonical_fact',
    }
    use_conversation_context = bool(payload.get('use_conversation_context'))
    return PublicInstitutionPlan(
        conversation_act=conversation_act,
        required_tools=required_tools,
        fetch_profile=fetch_profile,
        secondary_acts=secondary_acts,
        requested_attribute=requested_attribute,
        requested_channel=requested_channel,
        focus_hint=focus_hint,
        semantic_source='llm',
        use_conversation_context=use_conversation_context,
    )


def _apply_public_semantic_plan_overrides(
    message: str,
    semantic_plan: PublicInstitutionPlan | None,
) -> PublicInstitutionPlan | None:
    if semantic_plan is None:
        return None
    if _is_service_routing_query(message) and semantic_plan.conversation_act != 'service_routing':
        return replace(semantic_plan, conversation_act='service_routing')
    if _is_public_timeline_query(message) and semantic_plan.conversation_act != 'timeline':
        return replace(semantic_plan, conversation_act='timeline')
    if _is_public_policy_query(message) and semantic_plan.conversation_act != 'policy':
        return replace(semantic_plan, conversation_act='policy')
    if (
        _is_public_process_compare_query(message) or _is_public_bolsas_and_processes_query(message)
    ) and semantic_plan.conversation_act != 'policy_compare':
        return replace(semantic_plan, conversation_act='policy_compare')
    if _is_access_scope_query(message) and semantic_plan.conversation_act != 'access_scope':
        return replace(semantic_plan, conversation_act='access_scope')
    if (
        _is_assistant_identity_query(message)
        and semantic_plan.conversation_act != 'assistant_identity'
    ):
        return replace(semantic_plan, conversation_act='assistant_identity')
    if _is_public_enrichment_query(message) and semantic_plan.conversation_act != 'features':
        return replace(semantic_plan, conversation_act='features')
    if _is_public_scholarship_query(message) and semantic_plan.conversation_act != 'pricing':
        return replace(semantic_plan, conversation_act='pricing')
    requested_attributes = set(_requested_public_attributes(message))
    primary_entity = _primary_public_entity_hint(message)
    if (
        semantic_plan.conversation_act == 'operating_hours'
        and 'name' in requested_attributes
        and primary_entity not in {None, 'escola'}
        and 'features' not in semantic_plan.secondary_acts
    ):
        return replace(
            semantic_plan, secondary_acts=(*semantic_plan.secondary_acts[:1], 'features')
        )
    return semantic_plan


def _normalize_public_plan_for_message(
    *,
    message: str,
    conversation_context: dict[str, Any] | None,
    conversation_act: str,
    secondary_acts: tuple[str, ...],
    required_tools: list[str],
    fetch_profile: bool,
) -> tuple[str, tuple[str, ...], list[str], bool]:
    requested_attributes = set(_requested_public_attributes(message))
    primary_entity = _primary_public_entity_hint(message, conversation_context)
    normalized_act = conversation_act
    normalized_secondary = [
        act for act in secondary_acts if isinstance(act, str) and act and act != conversation_act
    ]
    normalized_tools = [
        tool_name for tool_name in required_tools if isinstance(tool_name, str) and tool_name
    ]
    normalized_fetch_profile = fetch_profile

    def ensure_tool(tool_name: str) -> None:
        if tool_name not in normalized_tools:
            normalized_tools.append(tool_name)

    if _is_public_document_submission_query(message):
        normalized_act = 'document_submission'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_process_compare_query(message) or _is_public_bolsas_and_processes_query(
        message
    ):
        normalized_act = 'policy_compare'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_policy_query(message):
        normalized_act = 'policy'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif (
        _is_follow_up_query(message)
        and isinstance(_recent_trace_focus(conversation_context), dict)
        and str((_recent_trace_focus(conversation_context) or {}).get('active_task', '')).strip()
        == 'public:document_submission'
    ):
        normalized_act = 'document_submission'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_teacher_identity_query(message):
        normalized_act = 'teacher_directory'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_teacher_directory_follow_up(message, conversation_context):
        normalized_act = 'teacher_directory'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _matches_public_contact_rule(message) or _requested_contact_channel(message) is not None:
        normalized_act = 'contacts'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _is_public_timeline_query(message):
        normalized_act = 'timeline'
        normalized_secondary = [act for act in normalized_secondary if act != 'calendar_events']
        normalized_tools = [
            tool_name for tool_name in normalized_tools if tool_name != 'get_public_calendar_events'
        ]
        ensure_tool('get_public_timeline')
        normalized_fetch_profile = True
    elif _is_public_calendar_event_query(message):
        normalized_act = 'calendar_events'
        normalized_tools = [
            tool_name for tool_name in normalized_tools if tool_name != 'get_public_timeline'
        ]
        ensure_tool('get_public_calendar_events')
        normalized_fetch_profile = True
    elif _is_public_capacity_query(message):
        normalized_act = 'capacity'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif _recent_messages_mention(
        conversation_context,
        {
            'aulas',
            'formatura',
            'reuniao com responsaveis',
            'reunião com responsáveis',
            'calendario',
            'calendário',
        },
    ) and any(
        _message_matches_term(_normalize_text(message), term)
        for term in {
            'ja comecaram',
            'já começaram',
            'ta longe',
            'está longe',
            'vai me avisar',
            'vão me avisar',
            'me avisa',
            'que dia e hoje',
            'que dia é hoje',
        }
    ):
        normalized_act = 'timeline'
        ensure_tool('get_public_timeline')
        normalized_fetch_profile = True

    if (
        _is_follow_up_query(message)
        and requested_attributes == {'name'}
        and primary_entity not in {None, 'escola'}
        and normalized_act not in {'contacts', 'leadership', 'teacher_directory'}
    ):
        normalized_act = 'features'
        ensure_tool('get_public_school_profile')
        normalized_fetch_profile = True
    elif (
        normalized_act == 'operating_hours'
        and 'name' in requested_attributes
        and primary_entity not in {None, 'escola'}
        and 'features' not in normalized_secondary
    ):
        normalized_secondary = ['features', *normalized_secondary]

    normalized_secondary = [act for act in normalized_secondary if act != normalized_act][:2]
    return normalized_act, tuple(normalized_secondary), normalized_tools, normalized_fetch_profile


async def _resolve_public_institution_plan(
    *,
    settings: Any,
    message: str,
    preview: Any,
    conversation_context: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
) -> PublicInstitutionPlan:
    semantic_plan: PublicInstitutionPlan | None = None
    if _should_run_public_semantic_resolver(
        message=message,
        preview=preview,
        conversation_context=conversation_context,
    ):
        payload: dict[str, Any] | None = None
        try:
            payload = await resolve_langgraph_public_semantic_with_provider(
                settings=settings,
                request_message=message,
                conversation_context=conversation_context,
                school_profile=school_profile,
                selected_tools=list(preview.selected_tools),
            )
        except Exception:
            payload = None
        semantic_plan = _normalize_public_semantic_plan(payload)
        semantic_plan = _apply_public_semantic_plan_overrides(message, semantic_plan)
    return _build_public_institution_plan(
        message,
        list(preview.selected_tools),
        semantic_plan=semantic_plan,
        conversation_context=conversation_context,
        school_profile=school_profile,
    )


def _build_public_institution_plan(
    message: str,
    selected_tools: list[str],
    semantic_plan: PublicInstitutionPlan | None = None,
    *,
    conversation_context: dict[str, Any] | None = None,
    school_profile: dict[str, Any] | None = None,
) -> PublicInstitutionPlan:
    _refresh_runtime_core_namespace()
    required_tools: list[str] = []
    secondary_acts: tuple[str, ...] = semantic_plan.secondary_acts if semantic_plan else ()

    def add(tool_name: str) -> None:
        if tool_name not in required_tools:
            required_tools.append(tool_name)

    conversation_act = semantic_plan.conversation_act if semantic_plan else 'canonical_fact'
    fetch_profile = semantic_plan.fetch_profile if semantic_plan else True
    if (
        _is_leadership_specific_query(message)
        and conversation_act == 'contacts'
        and (
            (
                semantic_plan
                and semantic_plan.requested_attribute
                in {'name', 'age', 'whatsapp', 'phone', 'email', 'contact'}
            )
            or _requested_public_attribute(message)
            in {'name', 'age', 'whatsapp', 'phone', 'email', 'contact'}
        )
    ):
        conversation_act = 'leadership'

    if semantic_plan is not None:
        for tool_name in semantic_plan.required_tools:
            add(tool_name)
        if not secondary_acts and _has_public_multi_intent_signal(message):
            matched_rules = _prioritize_public_act_rules(
                message,
                _matched_public_act_rules(message, conversation_context=conversation_context),
            )
            secondary_acts = tuple(
                rule.name for rule in matched_rules[:3] if rule.name != conversation_act
            )
    else:
        matched_rules = _prioritize_public_act_rules(
            message,
            _matched_public_act_rules(message, conversation_context=conversation_context),
        )
        if matched_rules:
            primary_rule = matched_rules[0]
            conversation_act = primary_rule.name
            fetch_profile = primary_rule.fetch_profile
            if _has_public_multi_intent_signal(message):
                secondary_acts = tuple(
                    rule.name for rule in matched_rules[1:3] if rule.name != conversation_act
                )
            for rule in matched_rules[:3]:
                for tool_name in rule.required_tools:
                    add(tool_name)
        else:
            matched_rule = _match_public_act_rule(message)
            if matched_rule is not None:
                conversation_act = matched_rule.name
                fetch_profile = matched_rule.fetch_profile
                for tool_name in matched_rule.required_tools:
                    add(tool_name)

    for tool_name in selected_tools:
        if tool_name == 'get_public_school_profile':
            continue
        add(tool_name)

    conversation_act, secondary_acts, required_tools, fetch_profile = (
        _normalize_public_plan_for_message(
            message=message,
            conversation_context=conversation_context,
            conversation_act=conversation_act,
            secondary_acts=secondary_acts,
            required_tools=required_tools,
            fetch_profile=fetch_profile,
        )
    )

    if conversation_act == 'assistant_identity':
        add('get_service_directory')

    if isinstance(school_profile, dict) and _requested_contact_channel(message):
        preferred_labels = _preferred_contact_labels_from_context(
            school_profile,
            message,
            conversation_context,
        )
        if _contact_is_general_school_query(message):
            preferred_labels = []
        if any(
            label in {'Orientacao educacional', 'Financeiro', 'Admissoes'}
            for label in preferred_labels
        ):
            add('get_service_directory')
        if any(label in {'Direcao', 'Coordenacao'} for label in preferred_labels):
            add('get_org_directory')

    if fetch_profile or (not required_tools and conversation_act != 'utility_date'):
        add('get_public_school_profile')
    if conversation_act == 'timeline' and not _has_public_multi_intent_signal(message):
        secondary_acts = ()

    plan = PublicInstitutionPlan(
        conversation_act=conversation_act,
        required_tools=tuple(required_tools),
        fetch_profile=fetch_profile,
        secondary_acts=secondary_acts,
        requested_attribute=semantic_plan.requested_attribute if semantic_plan else None,
        requested_channel=semantic_plan.requested_channel if semantic_plan else None,
        focus_hint=semantic_plan.focus_hint if semantic_plan else None,
        semantic_source=semantic_plan.semantic_source if semantic_plan else 'rules',
        use_conversation_context=semantic_plan.use_conversation_context if semantic_plan else False,
    )
    return _apply_public_open_documentary_plan(message, plan)


def _build_public_institution_specialists(
    plan: PublicInstitutionPlan,
) -> tuple[InternalSpecialistPlan, ...]:
    specialists: list[InternalSpecialistPlan] = []

    concierge_tools = tuple(
        tool_name
        for tool_name in plan.required_tools
        if tool_name in {'list_assistant_capabilities', 'get_service_directory'}
    )
    if (
        plan.conversation_act
        in {
            'greeting',
            'capabilities',
            'assistant_identity',
            'input_clarification',
            'scope_boundary',
            'service_routing',
        }
        or concierge_tools
    ):
        specialists.append(
            InternalSpecialistPlan(
                name='concierge',
                purpose='navegacao institucional, descoberta de capacidades e orientacao por setor',
                tool_names=concierge_tools,
            )
        )

    knowledge_tools = tuple(
        tool_name
        for tool_name in plan.required_tools
        if tool_name
        in {
            'get_public_school_profile',
            'get_org_directory',
            'get_public_timeline',
            'get_public_calendar_events',
        }
    )
    if knowledge_tools or not specialists:
        specialists.append(
            InternalSpecialistPlan(
                name='public_knowledge',
                purpose='fatos canonicos, lideranca, contatos e perfil publico da instituicao',
                tool_names=knowledge_tools,
            )
        )

    return tuple(specialists)


async def _execute_public_institution_plan(
    *,
    settings: Any,
    plan: PublicInstitutionPlan,
    school_profile: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str], list[str]]:
    profile = dict(school_profile or {}) if plan.fetch_profile else {}
    executed_tools: list[str] = []
    executed_specialists: list[str] = []

    for specialist in _build_public_institution_specialists(plan):
        executed_specialists.append(specialist.name)
        for tool_name in specialist.tool_names:
            if tool_name == 'get_public_school_profile':
                if not profile:
                    fetched_profile = await _fetch_public_school_profile(settings=settings)
                    if isinstance(fetched_profile, dict):
                        profile = dict(fetched_profile)
                executed_tools.append(tool_name)
                continue

            if tool_name == 'list_assistant_capabilities':
                capabilities = await _fetch_public_assistant_capabilities(settings=settings)
                if isinstance(capabilities, dict):
                    profile['assistant_capabilities'] = capabilities
                    profile.setdefault('school_name', capabilities.get('school_name'))
                    profile.setdefault('segments', capabilities.get('segments', []))
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_org_directory':
                directory = await _fetch_public_org_directory(settings=settings)
                if isinstance(directory, dict):
                    profile.setdefault('school_name', directory.get('school_name'))
                    profile['leadership_team'] = directory.get('leadership_team', [])
                    profile['contact_channels'] = directory.get('contact_channels', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_service_directory':
                directory = await _fetch_public_service_directory(settings=settings)
                if isinstance(directory, dict):
                    profile.setdefault('school_name', directory.get('school_name'))
                    profile['service_catalog'] = directory.get('services', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_public_timeline':
                timeline = await _fetch_public_timeline(settings=settings)
                if isinstance(timeline, dict):
                    profile.setdefault('school_name', timeline.get('school_name'))
                    profile['public_timeline'] = timeline.get('entries', [])
                executed_tools.append(tool_name)
                continue

            if tool_name == 'get_public_calendar_events':
                events = await _fetch_public_calendar_events(settings=settings)
                if events:
                    profile['public_calendar_events'] = events
                executed_tools.append(tool_name)
                continue

    return profile, executed_tools, executed_specialists


async def _fetch_public_calendar(*, settings: Any) -> list[CalendarEventCard]:
    today = date.today()
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/calendar/public',
        params={
            'date_from': today.isoformat(),
            'date_to': (today + timedelta(days=120)).isoformat(),
            'limit': 6,
        },
    )
    if status_code != 200 or payload is None:
        return []
    events = payload.get('events', [])
    if not isinstance(events, list):
        return []
    return [CalendarEventCard.model_validate(event) for event in events]


def _select_handoff_queue(message: str) -> str:
    normalized = _normalize_text(message)
    if any(term in normalized for term in SUPPORT_FINANCE_TERMS):
        return 'financeiro'
    if any(term in normalized for term in SUPPORT_COORDINATION_TERMS):
        return 'coordenacao'
    if any(term in normalized for term in SUPPORT_SECRETARIAT_TERMS):
        return 'secretaria'
    return 'atendimento'


def _build_handoff_summary(*, request: MessageResponseRequest, actor: dict[str, Any] | None) -> str:
    requester = 'Visitante do bot'
    if actor and isinstance(actor.get('full_name'), str):
        requester = str(actor['full_name'])

    message_excerpt = ' '.join(request.message.split())
    if len(message_excerpt) > 220:
        message_excerpt = f'{message_excerpt[:219].rstrip()}...'

    return (
        f'{requester} solicitou apoio humano pelo canal {request.channel.value}: {message_excerpt}'
    )


async def _create_support_handoff(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id
    if not conversation_external_id:
        conversation_external_id = (
            f'{request.channel.value}:{request.telegram_chat_id or "anonymous"}:handoff'
        )

    payload = {
        'conversation_external_id': conversation_external_id,
        'channel': request.channel.value,
        'queue_name': _select_handoff_queue(request.message),
        'summary': _build_handoff_summary(request=request, actor=actor),
        'telegram_chat_id': request.telegram_chat_id,
        'user_message': request.message,
    }
    response_payload, status_code = await _api_core_post(
        settings=settings,
        path='/v1/internal/support/handoffs',
        payload=payload,
    )
    if status_code != 200 or response_payload is None:
        return None
    return response_payload


def _extract_requested_date(message: str) -> date | None:
    normalized = _normalize_text(message)
    explicit_match = re.search(r'\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b', normalized)
    if explicit_match:
        day = int(explicit_match.group(1))
        month = int(explicit_match.group(2))
        year = explicit_match.group(3)
        if year is None:
            year_value = date.today().year
        else:
            year_value = int(year)
            if year_value < 100:
                year_value += 2000
        try:
            return date(year_value, month, day)
        except ValueError:
            return None

    weekday_map = {
        'segunda': 0,
        'terca': 1,
        'terça': 1,
        'quarta': 2,
        'quinta': 3,
        'sexta': 4,
        'sabado': 5,
        'sábado': 5,
    }
    today = date.today()
    for label, weekday in weekday_map.items():
        if _message_matches_term(normalized, label):
            offset = (weekday - today.weekday()) % 7
            if offset == 0:
                offset = 7
            return today + timedelta(days=offset)
    return None


def _weekday_label_for_date(value: date | None) -> str | None:
    if value is None:
        return None
    labels = {
        0: 'segunda-feira',
        1: 'terca-feira',
        2: 'quarta-feira',
        3: 'quinta-feira',
        4: 'sexta-feira',
        5: 'sabado',
        6: 'domingo',
    }
    return labels.get(value.weekday())


def _extract_requested_window(message: str) -> str | None:
    normalized = _normalize_text(message)
    time_match = re.search(r'\b(\d{1,2})(?:[:h](\d{2}))\b', normalized)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f'{hour:02d}:{minute:02d}'
    if 'manha' in normalized:
        return 'manha'
    if 'tarde' in normalized:
        return 'tarde'
    if 'noite' in normalized:
        return 'noite'
    return None
