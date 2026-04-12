from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Public act rule matching helpers extracted from public_orchestration_runtime.py."""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import _recent_trace_focus


LOCAL_EXTRACTED_NAMES = {
    '_intent_analysis_impl',
    '_is_greeting_only',
    '_is_auth_guidance_query',
    '_is_access_scope_query',
    '_is_language_preference_query',
    '_is_service_routing_query',
    '_is_assistant_identity_query',
    '_is_capability_query',
    '_is_comparative_query',
    '_looks_like_public_documentary_open_query',
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


def _normalize_text(message: str | None) -> str:
    return _intent_analysis_impl('_normalize_text')(message)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _is_greeting_only(message: str) -> bool:
    return _intent_analysis_impl('_is_greeting_only')(message)


def _is_auth_guidance_query(message: str) -> bool:
    return _intent_analysis_impl('_is_auth_guidance_query')(message)


def _is_access_scope_query(message: str) -> bool:
    return _intent_analysis_impl('_is_access_scope_query')(message)


def _is_language_preference_query(message: str) -> bool:
    return _intent_analysis_impl('_is_language_preference_query')(message)


def _is_service_routing_query(message: str) -> bool:
    return _intent_analysis_impl('_is_service_routing_query')(message)


def _is_assistant_identity_query(message: str) -> bool:
    return _intent_analysis_impl('_is_assistant_identity_query')(message)


def _is_capability_query(message: str) -> bool:
    return _intent_analysis_impl('_is_capability_query')(message)


def _is_comparative_query(message: str) -> bool:
    return _intent_analysis_impl('_is_comparative_query')(message)


def _looks_like_public_documentary_open_query(message: str) -> bool:
    from . import public_orchestration_runtime as _public_orchestration_runtime

    return _public_orchestration_runtime._looks_like_public_documentary_open_query(message)


def _public_profile_impl(name: str):
    from . import public_profile_runtime as _public_profile_runtime

    return getattr(_public_profile_runtime, name)


def _extract_public_curriculum_subject_focus(message: str) -> str | None:
    return _public_profile_impl('_extract_public_curriculum_subject_focus')(message)


def _requested_public_attribute(message: str) -> str | None:
    return _public_profile_impl('_requested_public_attribute')(message)


def _requested_contact_channel(message: str) -> str | None:
    return _public_profile_impl('_requested_contact_channel')(message)


def _requested_public_features(message: str) -> tuple[str, ...]:
    return _public_profile_impl('_requested_public_features')(message)


def _extract_public_curriculum_subject_focus(message: str) -> str | None:
    return _public_profile_impl('_extract_public_curriculum_subject_focus')(message)


def _count_public_contact_subjects(message: str) -> int:
    return _public_profile_impl('_count_public_contact_subjects')(message)


def _is_public_family_new_calendar_enrollment_query(message: str) -> bool:
    return _public_profile_impl('_is_public_family_new_calendar_enrollment_query')(message)


def _is_public_feature_query(message: str) -> bool:
    return _public_profile_impl('_is_public_feature_query')(message)


def _is_public_timeline_lifecycle_query(message: str) -> bool:
    return _public_profile_impl('_is_public_timeline_lifecycle_query')(message)


def _is_public_travel_planning_query(message: str) -> bool:
    return _public_profile_impl('_is_public_travel_planning_query')(message)


def _is_public_year_three_phase_query(message: str) -> bool:
    return _public_profile_impl('_is_public_year_three_phase_query')(message)


def _looks_like_teacher_internal_scope_query(message: str) -> bool:
    return _public_profile_impl('_looks_like_teacher_internal_scope_query')(message)


def _recent_public_feature_key(conversation_context: dict[str, Any] | None) -> str | None:
    return _public_profile_impl('_recent_public_feature_key')(conversation_context)


def _is_public_bolsas_and_processes_query(message: str) -> bool:
    return _public_profile_impl('_is_public_bolsas_and_processes_query')(message)


def _is_public_calendar_visibility_query(message: str) -> bool:
    return _public_profile_impl('_is_public_calendar_visibility_query')(message)


def _is_public_first_month_risks_query(message: str) -> bool:
    return _public_profile_impl('_is_public_first_month_risks_query')(message)


def _is_public_health_authorization_bridge_query(message: str) -> bool:
    return _public_profile_impl('_is_public_health_authorization_bridge_query')(message)


def _is_public_health_second_call_query(message: str) -> bool:
    return _public_profile_impl('_is_public_health_second_call_query')(message)


def _is_public_permanence_family_query(message: str) -> bool:
    return _public_profile_impl('_is_public_permanence_family_query')(message)


def _is_public_process_compare_query(message: str) -> bool:
    return _public_profile_impl('_is_public_process_compare_query')(message)


def _is_public_timeline_before_after_query(message: str) -> bool:
    return _public_profile_impl('_is_public_timeline_before_after_query')(message)


def _contains_any(message: str, terms: set[str]) -> bool:
    return _intent_analysis_impl('_contains_any')(message, terms)


def _is_follow_up_query(message: str) -> bool:
    return _intent_analysis_impl('_is_follow_up_query')(message)


def _is_public_pricing_navigation_query(message: str) -> bool:
    return _intent_analysis_impl('_is_public_pricing_navigation_query')(message)


def _matches_public_contact_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'canais', 'canal', 'falar'}) and (
        _count_public_contact_subjects(message) >= 1
    ):
        return True
    return False


def _matches_public_location_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS)


def _matches_public_confessional_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_CONFESSIONAL_TERMS)


def _matches_public_kpi_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_KPI_TERMS)


def _is_cross_document_public_query(message: str) -> bool:
    if _is_public_policy_compare_query(message) or _is_public_family_new_calendar_enrollment_query(
        message
    ):
        return False
    normalized = _normalize_text(message)
    has_synthesis_signal = any(
        _message_matches_term(normalized, term) for term in PUBLIC_CROSS_DOCUMENT_TERMS
    ) or any(
        phrase in normalized
        for phrase in (
            'o que uma familia precisa entender',
            'o que uma família precisa entender',
            'uma unica explicacao coerente',
            'uma única explicação coerente',
            'temas atravessam varios documentos',
            'temas atravessam vários documentos',
            'guia de sobrevivencia do primeiro mes',
            'guia de sobrevivência do primeiro mês',
        )
    )
    if not has_synthesis_signal:
        return False
    return any(_message_matches_term(normalized, term) for term in PUBLIC_CROSS_DOCUMENT_DOC_TERMS)


def _matches_public_highlight_rule(message: str) -> bool:
    if _is_cross_document_public_query(message):
        return False
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_HIGHLIGHT_TERMS):
        return True
    return any(
        phrase in normalized
        for phrase in (
            'se eu fosse uma familia nova',
            'se eu fosse uma família nova',
            'por que eu colocaria meus filhos',
            'por que deveria colocar meus filhos',
        )
    )


def _matches_public_visit_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_VISIT_TERMS)


def _matches_public_pricing_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    hints = resolve_entity_hints(message)
    if _is_public_pricing_navigation_query(message):
        return True
    return (
        hints.is_hypothetical
        and bool(hints.quantity_hint)
        and any(_message_matches_term(normalized, term) for term in {'matricula', 'matrícula'})
    )


def _matches_public_schedule_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SCHEDULE_TERMS)


def _matches_public_feature_rule(message: str) -> bool:
    return _is_public_feature_query(message)


def _matches_public_segment_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SEGMENT_TERMS)


def _is_leadership_specific_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return False
    return _requested_public_attribute(message) is not None


def _is_public_calendar_event_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'proximo evento',
            'próximo evento',
            'proxima reuniao',
            'próxima reunião',
            'reuniao de pais',
            'reunião de pais',
            'reuniao geral',
            'reunião geral',
            'mostra de ciencias',
            'mostra de ciências',
            'plantao pedagogico',
            'plantão pedagógico',
            'visita guiada',
        }
    ):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {'quando', 'qual data', 'que dia', 'quando vai ser', 'quando acontece'}
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'reuniao',
            'reunião',
            'evento',
            'mostra',
            'feira',
            'plantao',
            'plantão',
            'visita guiada',
            'cerimonia',
            'cerimônia',
        }
    )


def _is_public_capacity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_capacity_signal = any(
        _message_matches_term(normalized, term)
        for term in (
            *PUBLIC_CAPACITY_STUDENT_TERMS,
            *PUBLIC_CAPACITY_PARKING_TERMS,
            'vaga',
            'vagas',
        )
    )
    if not has_capacity_signal:
        return False
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_PARKING_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_STUDENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'vaga', 'vagas'}):
        if any(
            phrase in normalized
            for phrase in {
                'quantas vagas',
                'quanta vaga',
                'tem vagas',
                'tem vaga',
                'ha vagas',
                'há vagas',
            }
        ):
            return True
        if any(
            _message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_DISAMBIGUATION_TERMS
        ):
            return True
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'trabalhar',
                'trabalhe conosco',
                'dar aula',
                'curriculo',
                'currículo',
                'processo seletivo',
            }
        ):
            return False
    return False


def _is_public_careers_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _looks_like_teacher_internal_scope_query(message):
        return False
    if _is_public_capacity_query(message):
        return False
    return any(_message_matches_term(normalized, term) for term in TEACHER_RECRUITMENT_TERMS)


def _is_public_curriculum_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        return True
    if _extract_public_curriculum_subject_focus(message) is not None:
        return True
    if any(_message_matches_term(normalized, term) for term in ACADEMIC_DIFFICULTY_TERMS) and any(
        _message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_SCOPE_TERMS
    ):
        return True
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {
            'disciplina',
            'disciplinas',
            'convivencia',
            'convivência',
            'aprendizagem',
            'rotina',
        }
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {'materia', 'materias', 'disciplina', 'disciplinas'}
    ) and any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'fundamental',
            'fundamental i',
            'fundamental ii',
            'anos iniciais',
            'base curricular',
            'curriculo',
            'currículo',
        }
    )


def _is_public_date_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_UTILITY_DATE_TERMS)


def _is_public_document_submission_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_DOCUMENT_SUBMISSION_TERMS):
        return True
    document_terms = {'documento', 'documentos', 'matricula', 'matrícula', 'cadastro'}
    digital_terms = {
        'online',
        'digital',
        'portal',
        'email',
        'e-mail',
        'enviar',
        'envio',
        'mandar',
        'mando',
    }
    special_channel_terms = {'fax', 'telegrama', 'caixa postal'}
    if any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in special_channel_terms
    ):
        return True
    return any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in digital_terms
    )


def _is_public_operating_hours_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_OPERATING_HOURS_TERMS):
        return True
    return _contains_any(
        normalized, {'abre', 'abertura', 'funciona', 'fecha', 'fechamento'}
    ) and _contains_any(
        normalized,
        {'amanha', 'amanhã', 'cedo', 'horas', 'hora', 'horario', 'horário'},
    )


def _is_public_policy_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    mentions_compare = any(
        _message_matches_term(normalized, term)
        for term in {
            'compare',
            'comparar',
            'comparacao',
            'comparação',
            'como os dois se complementam',
        }
    )
    mentions_general_rules = any(
        _message_matches_term(normalized, term)
        for term in {'manual de regulamentos gerais', 'regulamentos gerais', 'manual geral'}
    )
    mentions_eval_policy = any(
        _message_matches_term(normalized, term)
        for term in {
            'politica de avaliacao',
            'política de avaliação',
            'avaliacao e promocao',
            'avaliação e promoção',
        }
    )
    return mentions_compare and mentions_general_rules and mentions_eval_policy


def _is_public_policy_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_POLICY_TERMS):
        return True
    if 'projeto de vida' in normalized:
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'avaliacao',
            'avaliação',
            'recuperacao',
            'recuperação',
            'promocao',
            'promoção',
            'aprovacao',
            'aprovação',
        }
    ):
        return any(
            _message_matches_term(normalized, term)
            for term in {'politica', 'política', 'como funciona', 'regra', 'regras', 'funciona'}
        )
    if any(
        _message_matches_term(normalized, term)
        for term in {'falta', 'faltas', 'frequencia', 'frequência'}
    ):
        return any(
            _message_matches_term(normalized, term)
            for term in {
                'politica',
                'política',
                'regra',
                'regras',
                '75%',
                'minima',
                'mínima',
                'o que acontece',
            }
        )
    return False


def _is_public_school_name_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        term in normalized
        for term in {
            'nome da escola',
            'nome do colegio',
            'nome do colégio',
            'como se chama a escola',
            'como se chama o colegio',
            'como se chama o colégio',
        }
    )


def _is_public_service_credentials_bundle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if (
        'credenciais' not in normalized
        and 'credencial' not in normalized
        and 'login' not in normalized
        and 'senha' not in normalized
        and 'aplicativo' not in normalized
        and 'app' not in normalized
    ):
        return False
    has_service_anchor = any(
        _message_matches_term(normalized, term)
        for term in {
            'secretaria',
            'portal',
            'aplicativo',
            'app',
            'documentos',
            'documentacao',
            'documentação',
            'cadastro',
        }
    )
    return has_service_anchor


def _is_public_social_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SOCIAL_TERMS)


def _is_public_teacher_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'prof', 'professor', 'professora', 'docente'}
    ):
        return False
    if _requested_public_attribute(message) in {'name', 'whatsapp', 'email', 'phone', 'contact'}:
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'falar com',
            'quero falar com',
            'conversar com',
            'falar direto com',
            'falar diretamente com',
        }
    )


def _is_public_timeline_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _is_public_timeline_lifecycle_query(message):
        return True
    if _is_public_travel_planning_query(message):
        return True
    if _is_public_year_three_phase_query(message):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'comeco',
            'começo',
            'quando fecha',
            'inicio',
            'início',
            'abertura',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
        }
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'matrícula',
            'formatura',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    )


def _is_public_web_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_WEB_TERMS)


PUBLIC_ACT_RULES: tuple[PublicActRule, ...] = (
    PublicActRule('greeting', _is_greeting_only, ('list_assistant_capabilities',), False),
    PublicActRule('utility_date', _is_public_date_query, (), False),
    PublicActRule('auth_guidance', _is_auth_guidance_query, (), False),
    PublicActRule('access_scope', _is_access_scope_query, ('list_assistant_capabilities',), False),
    PublicActRule(
        'language_preference', _is_language_preference_query, ('get_public_school_profile',), False
    ),
    PublicActRule('service_routing', _is_service_routing_query, ('get_service_directory',), False),
    PublicActRule(
        'service_credentials_bundle',
        _is_public_service_credentials_bundle_query,
        ('get_service_directory',),
        False,
    ),
    PublicActRule(
        'assistant_identity', _is_assistant_identity_query, ('get_org_directory',), False
    ),
    PublicActRule('capabilities', _is_capability_query, ('list_assistant_capabilities',), False),
    PublicActRule('document_submission', _is_public_document_submission_query),
    PublicActRule('policy', _is_public_policy_query, ('get_public_school_profile',), False),
    PublicActRule(
        'policy_compare', _is_public_policy_compare_query, ('get_public_school_profile',), False
    ),
    PublicActRule('capacity', _is_public_capacity_query, ('get_public_school_profile',), False),
    PublicActRule('careers', _is_public_careers_query, ('get_service_directory',)),
    PublicActRule('teacher_directory', _is_public_teacher_identity_query),
    PublicActRule('leadership', _is_leadership_specific_query, ('get_org_directory',), False),
    PublicActRule('web_presence', _is_public_web_query),
    PublicActRule('social_presence', _is_public_social_query),
    PublicActRule('contacts', _matches_public_contact_rule, ('get_org_directory',)),
    PublicActRule('comparative', _is_comparative_query),
    PublicActRule('operating_hours', _is_public_operating_hours_query),
    PublicActRule('timeline', _is_public_timeline_query, ('get_public_timeline',), False),
    PublicActRule(
        'calendar_events', _is_public_calendar_event_query, ('get_public_calendar_events',), False
    ),
    PublicActRule('location', _matches_public_location_rule),
    PublicActRule('confessional', _matches_public_confessional_rule),
    PublicActRule('curriculum', _is_public_curriculum_query),
    PublicActRule('kpi', _matches_public_kpi_rule),
    PublicActRule('highlight', _matches_public_highlight_rule),
    PublicActRule('visit', _matches_public_visit_rule),
    PublicActRule('pricing', _matches_public_pricing_rule),
    PublicActRule('schedule', _matches_public_schedule_rule),
    PublicActRule('features', _matches_public_feature_rule),
    PublicActRule('segments', _matches_public_segment_rule),
    PublicActRule('school_name', _is_public_school_name_query),
)


def _match_public_act_rule(message: str) -> PublicActRule | None:
    _refresh_runtime_core_namespace()
    for rule in PUBLIC_ACT_RULES:
        try:
            if rule.matcher(message):
                return rule
        except Exception:
            continue
    return None


def _matched_public_act_rules(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> tuple[PublicActRule, ...]:
    _refresh_runtime_core_namespace()
    matched: list[PublicActRule] = []
    for rule in PUBLIC_ACT_RULES:
        try:
            if rule.matcher(message):
                matched.append(rule)
        except Exception:
            continue
    normalized = _normalize_text(message)
    recent_feature_key = _recent_public_feature_key(conversation_context)
    if (
        recent_feature_key
        and _is_follow_up_query(message)
        and (
            any(_message_matches_term(normalized, term) for term in PUBLIC_SCHEDULE_TERMS)
            or bool(_requested_contact_channel(message))
            or _message_matches_term(normalized, 'nome')
        )
    ):
        feature_rule = next((rule for rule in PUBLIC_ACT_RULES if rule.name == 'features'), None)
        if feature_rule is not None and all(rule.name != 'features' for rule in matched):
            matched.append(feature_rule)
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if (
        isinstance(recent_focus, dict)
        and str(recent_focus.get('active_task', '')).strip() == 'public:features'
        and _is_follow_up_query(message)
    ):
        feature_rule = next((rule for rule in PUBLIC_ACT_RULES if rule.name == 'features'), None)
        if feature_rule is not None and all(rule.name != 'features' for rule in matched):
            matched.append(feature_rule)
    return tuple(matched)


def _has_public_multi_intent_signal(message: str) -> bool:
    normalized = _normalize_text(message)
    collapsed = re.sub(r'\s+', ' ', normalized).strip()
    collapsed_without_leading_connector = re.sub(
        r'^(e|tambem|tambem,|alem disso)\s+', '', collapsed
    ).strip()
    if re.match(r'^(quando|qual|quais|quem|onde|como|o que|que|por que)\s+e\b', collapsed):
        return False
    if re.match(
        r'^(quando|qual|quais|quem|onde|como|o que|que|por que)\s+e\b',
        collapsed_without_leading_connector,
    ):
        return False
    if collapsed.startswith('e ') and ' e ' not in collapsed_without_leading_connector:
        return False
    return any(
        marker in collapsed_without_leading_connector
        for marker in (
            ' e ',
            ', e ',
            ' alem de ',
            ' além de ',
            ' tambem ',
            ' também ',
        )
    )


def _prioritize_public_act_rules(
    message: str,
    matched_rules: tuple[PublicActRule, ...],
) -> tuple[PublicActRule, ...]:
    _refresh_runtime_core_namespace()
    if len(matched_rules) < 2:
        return matched_rules
    if _looks_like_public_documentary_open_query(message):
        blocked = {'comparative', 'highlight', 'features', 'curriculum'}
        filtered_rules = tuple(rule for rule in matched_rules if rule.name not in blocked)
        if filtered_rules:
            matched_rules = filtered_rules

    feature_requested = bool(_requested_public_features(message))
    channel_requested = _requested_contact_channel(message) is not None
    base_priority = {
        'greeting': 100,
        'utility_date': 100,
        'auth_guidance': 95,
        'access_scope': 94,
        'language_preference': 95,
        'scope_boundary': 95,
        'assistant_identity': 95,
        'service_routing': 95,
        'capabilities': 90,
        'policy': 89,
        'comparative': 89,
        'document_submission': 88,
        'capacity': 88,
        'careers': 88,
        'teacher_directory': 88,
        'leadership': 86,
        'contacts': 84,
        'social_presence': 83,
        'web_presence': 82,
        'location': 82,
        'curriculum': 82,
        'calendar_events': 82,
        'timeline': 81,
        'features': 80,
        'operating_hours': 70,
        'schedule': 65,
        'pricing': 64,
        'visit': 64,
        'kpi': 62,
        'highlight': 62,
        'segments': 58,
        'school_name': 56,
        'confessional': 54,
    }

    ranked: list[tuple[int, int, PublicActRule]] = []
    for index, rule in enumerate(matched_rules):
        score = base_priority.get(rule.name, 40)
        if rule.name == 'features' and feature_requested:
            score += 18
        if rule.name == 'schedule' and feature_requested:
            score -= 18
        if rule.name == 'contacts' and channel_requested:
            score += 8
        ranked.append((-score, index, rule))

    ranked.sort()
    return tuple(rule for _score, _index, rule in ranked)


PUBLIC_SEMANTIC_ACTS = {
    'greeting',
    'auth_guidance',
    'access_scope',
    'language_preference',
    'scope_boundary',
    'assistant_identity',
    'capabilities',
    'service_routing',
    'document_submission',
    'policy',
    'careers',
    'teacher_directory',
    'leadership',
    'contacts',
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
    'segments',
    'school_name',
    'timeline',
    'calendar_events',
    'utility_date',
    'canonical_fact',
}
PUBLIC_SEMANTIC_TOOLS = {
    'get_public_school_profile',
    'list_assistant_capabilities',
    'get_org_directory',
    'get_service_directory',
    'get_public_timeline',
    'get_public_calendar_events',
}


