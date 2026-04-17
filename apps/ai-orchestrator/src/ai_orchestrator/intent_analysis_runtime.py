from __future__ import annotations

import unicodedata

# ruff: noqa: F401,F403,F405
"""Intent analysis and preview-building helpers extracted from runtime_core.py."""

from . import runtime_core as _runtime_core


def _direct_normalize_text(message: str | None) -> str:
    normalized = unicodedata.normalize('NFKD', str(message or ''))
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _normalize_text(message: str | None) -> str:
    return _direct_normalize_text(message)


def _extract_requested_date(message: str):
    from .public_orchestration_runtime import _extract_requested_date as _impl

    return _impl(message)


def _recent_slot_value(conversation_context: dict[str, Any] | None, key: str) -> str | None:
    from .conversation_focus_runtime import _recent_slot_value as _impl

    return _impl(conversation_context, key)


def _public_profile_impl(name: str):
    from . import public_profile_runtime as _public_profile_runtime

    return getattr(_public_profile_runtime, name)


def _is_public_process_compare_query(message: str) -> bool:
    return _public_profile_impl('_is_public_process_compare_query')(message)


def _is_public_bolsas_and_processes_query(message: str) -> bool:
    return _public_profile_impl('_is_public_bolsas_and_processes_query')(message)


def _extract_grade_reference(message: str) -> str | None:
    return _public_profile_impl('_extract_grade_reference')(message)


def _requested_contact_channel(message: str) -> str | None:
    return _public_profile_impl('_requested_contact_channel')(message)


def _contact_is_general_school_query(message: str) -> bool:
    return _public_profile_impl('_contact_is_general_school_query')(message)


def _requested_public_features(message: str) -> tuple[str, ...]:
    return _public_profile_impl('_requested_public_features')(message)


def _select_public_segment(message: str) -> str | None:
    return _public_profile_impl('_select_public_segment')(message)


def _extract_public_curriculum_subject_focus(message: str) -> str | None:
    return _public_profile_impl('_extract_public_curriculum_subject_focus')(message)


def _compose_public_comparative_answer(profile: dict[str, Any]) -> str:
    return _public_profile_impl('_compose_public_comparative_answer')(profile)


def _is_public_curriculum_query(message: str) -> bool:
    return _public_profile_impl('_is_public_curriculum_query')(message)


def _is_public_document_submission_query(message: str) -> bool:
    return _public_profile_impl('_is_public_document_submission_query')(message)


def _student_scope_impl(name: str):
    from . import student_scope_runtime as _student_scope_runtime

    return getattr(_student_scope_runtime, name)


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    return _student_scope_impl('_linked_students')(actor)


def _is_access_scope_repair_query(
    message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> bool:
    return _student_scope_impl('_is_access_scope_repair_query')(message, actor, conversation_context)


def _is_admin_finance_combined_query(message: str) -> bool:
    from .conversation_focus_runtime import _is_admin_finance_combined_query as _impl

    return _impl(message)


def _protected_domain_impl(name: str):
    from . import protected_domain_runtime as _protected_domain_runtime

    return getattr(_protected_domain_runtime, name)


def _protected_summary_impl(name: str):
    from . import protected_summary_runtime as _protected_summary_runtime

    return getattr(_protected_summary_runtime, name)


def _detect_academic_focus_kind(message: str) -> str | None:
    return _protected_domain_impl('_detect_academic_focus_kind')(message)


def _looks_like_finance_open_amount_query(message: str) -> bool:
    return _protected_domain_impl('_looks_like_finance_open_amount_query')(message)


def _looks_like_academic_difficulty_query(message: str, conversation_context: dict[str, Any] | None = None) -> bool:
    return _protected_domain_impl('_looks_like_academic_difficulty_query')(message, conversation_context=conversation_context)


def _should_inherit_academic_attribute_from_context(message: str, conversation_context: dict[str, Any] | None) -> bool:
    return _protected_domain_impl('_should_inherit_academic_attribute_from_context')(
        message, conversation_context=conversation_context
    )


def _detect_finance_status_filter(message: str) -> set[str] | None:
    return _protected_summary_impl('_detect_finance_status_filter')(message)


def _looks_like_family_academic_aggregate_query(message: str) -> bool:
    return _protected_summary_impl('_looks_like_family_academic_aggregate_query')(message)


def _looks_like_family_attendance_aggregate_query(message: str) -> bool:
    return _protected_summary_impl('_looks_like_family_attendance_aggregate_query')(message)


def _looks_like_family_attendance_student_focus_followup(
    actor: dict[str, Any] | None,
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    return _protected_summary_impl('_looks_like_family_attendance_student_focus_followup')(
        actor,
        message,
        conversation_context=conversation_context,
    )


def _looks_like_family_finance_aggregate_query(message: str) -> bool:
    return _protected_summary_impl('_looks_like_family_finance_aggregate_query')(message)


def _looks_like_academic_progression_query(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    return _protected_summary_impl('_looks_like_academic_progression_query')(
        message,
        conversation_context=conversation_context,
    )


def _wants_attendance_timeline(message: str) -> bool:
    return _protected_summary_impl('_wants_attendance_timeline')(message)


def _wants_profile_update_guidance(message: str) -> bool:
    return _protected_summary_impl('_wants_profile_update_guidance')(message)


def _wants_upcoming_assessments(message: str) -> bool:
    return _protected_summary_impl('_wants_upcoming_assessments')(message)


def _export_runtime_core_namespace() -> None:
    existing_names = set(globals())
    for name, value in vars(_runtime_core).items():
        if name.startswith('__') or name in existing_names:
            continue
        globals()[name] = value


_export_runtime_core_namespace()
_normalize_text = _direct_normalize_text


def _is_assistant_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    normalized_simple = normalized.strip(' ?.!')
    if normalized_simple in {'com quem eu falo', 'pra quem eu falo', 'para quem eu falo'}:
        return True
    if any(_message_matches_term(normalized, term) for term in SERVICE_ROUTING_TERMS):
        return False
    return any(_message_matches_term(normalized, term) for term in ASSISTANT_IDENTITY_TERMS)


def _is_capability_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in ASSISTANT_CAPABILITY_TERMS)


def _is_access_scope_query(message: str) -> bool:
    normalized = _normalize_text(message)
    explicit_scope_markers = (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'quais alunos estao vinculados a esta conta',
                'quais alunos estão vinculados a esta conta',
                'quais alunos estao vinculados nessa conta',
                'quais alunos estão vinculados nessa conta',
                'quais alunos estao vinculados nesta conta',
                'quais alunos estão vinculados nesta conta',
                'quem esta vinculado a esta conta',
                'quem está vinculado a esta conta',
                'quem esta vinculado nesta conta',
                'quem está vinculado nesta conta',
                'o que eu consigo ver sobre cada um',
                'o que consigo ver sobre cada um',
                'o que eu posso ver sobre cada um',
                'o que posso ver sobre cada um',
                'o que eu consigo consultar aqui',
                'o que consigo consultar aqui',
            }
        )
        or ('consigo ver' in normalized and 'exatamente' in normalized)
        or any(_message_matches_term(normalized, term) for term in ACCESS_SCOPE_TERMS)
    )
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'escopo do projeto',
            'sair do escopo',
            'fora do escopo',
            'dentro do escopo',
            'escopo escolar',
        }
    ):
        return explicit_scope_markers
    return explicit_scope_markers


def _should_prioritize_protected_sql_query(
    message: str,
    *,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    normalized = _normalize_text(message)
    if actor_role == 'teacher' and any(
        _message_matches_term(normalized, term)
        for term in {
            'minha alocacao docente',
            'minha alocação docente',
            'alocacao docente atual',
            'alocação docente atual',
            'minhas turmas',
            'minhas disciplinas',
            'turmas e disciplinas',
            'grade docente',
            'meu horario docente',
            'meu horário docente',
        }
    ):
        return True
    if not isinstance(actor, dict) or not _linked_students(actor):
        return False
    if _is_public_pricing_navigation_query(message) or _is_public_pricing_context_follow_up(
        message,
        conversation_context=conversation_context,
    ):
        return False
    if _is_public_curriculum_query(message) or _is_public_curriculum_context_follow_up(
        message,
        conversation_context=conversation_context,
    ):
        return False
    if _is_access_scope_query(message) or _is_access_scope_repair_query(
        message,
        actor,
        conversation_context,
    ):
        return False
    if _is_admin_finance_combined_query(message):
        return True
    if _looks_like_family_admin_aggregate_query(message):
        return True
    if _looks_like_family_finance_aggregate_query(message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'paguei parte da mensalidade',
            'negociar o restante',
            'mensalidade parcialmente paga',
            'minha situacao financeira',
            'minha situação financeira',
            'separando mensalidade',
            'taxa, atraso e desconto',
            'taxa atraso e desconto',
            'em aberto',
            'atraso',
            'atrasos',
            'desconto',
            'descontos',
        }
    ):
        return True
    if _looks_like_family_attendance_aggregate_query(message):
        return True
    if _looks_like_family_academic_aggregate_query(message):
        return True
    if _wants_upcoming_assessments(message) or _wants_attendance_timeline(message):
        return True
    if (
        _effective_finance_attribute_request(message, conversation_context=conversation_context)
        is not None
    ):
        return True
    if (
        _effective_finance_status_filter(message, conversation_context=conversation_context)
        is not None
    ):
        return True
    if (
        _effective_academic_attribute_request(message, conversation_context=conversation_context)
        is not None
    ):
        return True
    if _looks_like_academic_progression_query(
        message,
        conversation_context=conversation_context,
    ):
        return True
    if _looks_like_academic_difficulty_query(message, conversation_context=conversation_context):
        return True
    focus_kind = _detect_academic_focus_kind(message)
    if focus_kind is not None and focus_kind != 'grades':
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'media minima',
            'média mínima',
            'menores medias',
            'menores médias',
            'menor media',
            'menor média',
            'mais vulneravel',
            'mais vulnerável',
            'faltas recentes',
            'proximas provas',
            'próximas provas',
            'proximas avaliacoes',
            'próximas avaliações',
            'provas e entregas',
            'panorama combinado de documentacao e financeiro',
        }
    )


def _is_actor_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in ACTOR_IDENTITY_TERMS)


def _is_auth_guidance_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in AUTH_GUIDANCE_TERMS)


def _is_language_preference_query(message: str) -> bool:
    return looks_like_language_preference_feedback(message)


def _is_public_pricing_navigation_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if (
        _is_public_process_compare_query(message)
        or _is_public_bolsas_and_processes_query(message)
        or _is_access_scope_query(message)
    ):
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'minha situacao financeira',
            'minha situação financeira',
            'situacao financeira como se eu fosse leigo',
            'situação financeira como se eu fosse leigo',
            'paguei parte da mensalidade',
            'negociar o restante',
            'mensalidade parcialmente paga',
            'parcialmente paga',
            'o que ja aparece',
            'o que já aparece',
            'taxa',
            'atraso',
            'atrasos',
            'desconto',
            'descontos',
            'em aberto',
            'vencida',
            'vencidas',
            'proximo passo',
            'próximo passo',
        }
    ):
        return False
    entity_hints = resolve_entity_hints(message)
    if entity_hints.domain_hint == 'public_pricing':
        return True
    if any(_message_matches_term(normalized, term) for term in {'matricula', 'matrícula'}) and any(
        _message_matches_term(normalized, term)
        for term in {
            'por mes',
            'por mês',
            'mensalidade',
            'mensalidades',
            'filhos',
            'alunos',
            'total',
            'quanto fica',
            'quanto vira',
            'quanto custa',
        }
    ):
        return True
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_PRICING_TERMS):
        return False
    return not any(
        _message_matches_term(normalized, term)
        for term in {'meu', 'minha', 'meus', 'minhas', 'do meu filho', 'da minha filha'}
    )


def _looks_like_family_admin_aggregate_query(message: str) -> bool:
    normalized = _normalize_text(message)
    explicit_terms = {
        'documentacao dos meus filhos',
        'documentação dos meus filhos',
        'compare a documentacao dos meus filhos',
        'compare a documentação dos meus filhos',
        'compare a documentacao dos meus filhos e diga qual deles ainda tem pendencia',
        'compare a documentação dos meus filhos e diga qual deles ainda tem pendência',
        'quadro documental dos meus filhos',
        'quadro documental da familia',
        'pendencia documental dos meus filhos',
        'pendência documental dos meus filhos',
        'pendencias documentais dos meus filhos',
        'pendências documentais dos meus filhos',
    }
    if any(term in normalized for term in explicit_terms):
        return True
    has_family_anchor = any(
        term in normalized
        for term in {
            'meus filhos',
            'meus dois filhos',
            'minha familia',
            'minha família',
            'familia',
            'família',
            'contas vinculadas',
        }
    )
    has_admin_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'documentacao',
            'documentação',
            'documental',
            'documentais',
            'cadastro',
            'pendencia',
            'pendência',
            'pendencias',
            'pendências',
            'comprovante',
            'comprovantes',
            'administrativo',
            'administrativa',
        }
    )
    return has_family_anchor and has_admin_focus


def _is_explicit_public_pricing_projection_query(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if _is_public_process_compare_query(message) or _is_public_bolsas_and_processes_query(message):
        return False
    normalized = _normalize_text(message)
    entity_hints = resolve_entity_hints(message)
    quantity_hint = entity_hints.quantity_hint
    if quantity_hint is None and _is_public_pricing_context_follow_up(
        message, conversation_context=conversation_context
    ):
        quantity_hint = (
            int(_recent_slot_value(conversation_context, 'public_pricing_quantity') or 0) or None
        )
    if not quantity_hint:
        return False
    wants_enrollment = any(
        _message_matches_term(normalized, term)
        for term in {'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula'}
    )
    wants_monthly = any(
        _message_matches_term(normalized, term)
        for term in {'por mes', 'por mês', 'mensalidade', 'mensalidades'}
    )
    hypothetical_language = entity_hints.is_hypothetical or any(
        _message_matches_term(normalized, term)
        for term in {
            'quanto eu pagaria',
            'quanto daria',
            'quanto ficaria',
            'quanto sairia',
            'para ',
        }
    )
    return bool(
        _is_public_pricing_navigation_query(message)
        and hypothetical_language
        and (wants_monthly or wants_enrollment)
    )


def _extract_public_pricing_grade_year(message: str) -> str | None:
    grade_reference = _extract_grade_reference(message)
    if grade_reference:
        return grade_reference
    normalized = _normalize_text(message).strip()
    short_match = re.fullmatch(r'(1o|2o|3o|6o|7o|8o|9o)', normalized)
    if short_match:
        return f'{short_match.group(1)} ano'
    embedded_match = re.search(r'\b(1o|2o|3o|6o|7o|8o|9o)\b', normalized)
    if embedded_match:
        return f'{embedded_match.group(1)} ano'
    return None


def _detect_public_pricing_price_kind(message: str) -> str | None:
    normalized = _normalize_text(message)
    wants_enrollment_fee = any(
        _message_matches_term(normalized, term)
        for term in {'matricula', 'matrícula', 'taxa de matricula', 'taxa de matrícula'}
    )
    wants_monthly_amount = any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'mensalidades',
            'por mes',
            'por mês',
            'total por mes',
            'total por mês',
        }
    )
    if wants_monthly_amount and not wants_enrollment_fee:
        return 'monthly_amount'
    if wants_enrollment_fee:
        return 'enrollment_fee'
    return None


def _should_reuse_public_pricing_slots(message: str) -> bool:
    normalized = _normalize_text(message).strip()
    if not normalized:
        return False
    if _looks_like_explicit_non_pricing_public_switch(message):
        return False
    if _is_public_pricing_navigation_query(message):
        return False
    if _is_follow_up_query(message):
        return True
    if len(normalized) <= 24 and (
        _extract_public_pricing_grade_year(message) is not None
        or _select_public_segment(message) is not None
        or resolve_entity_hints(message).quantity_hint is not None
        or _detect_public_pricing_price_kind(message) is not None
    ):
        return True
    return False


def _looks_like_explicit_non_pricing_public_switch(message: str) -> bool:
    from .public_act_rules_runtime import (
        _is_leadership_specific_query,
        _is_public_capacity_query,
        _is_public_curriculum_query,
        _is_public_document_submission_query,
        _is_public_feature_query,
        _is_public_policy_query,
        _is_public_timeline_lifecycle_query,
        _is_public_timeline_query,
        _matches_public_contact_rule,
        _matches_public_location_rule,
    )

    if any(
        matcher(message)
        for matcher in (
            _is_public_document_submission_query,
            _is_public_timeline_query,
            _is_public_timeline_lifecycle_query,
            _matches_public_contact_rule,
            _matches_public_location_rule,
            _is_leadership_specific_query,
            _is_public_curriculum_query,
            _is_public_capacity_query,
            _is_public_feature_query,
            _is_public_policy_query,
        )
    ):
        return True

    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'biblioteca',
            'biblioteca aurora',
            'que horas fecha a biblioteca',
            'fecha a biblioteca',
            'quando iniciam as aulas',
            'quando comecam as aulas',
            'quando começam as aulas',
            'inicio das aulas',
            'início das aulas',
            'contato do diretor',
            'contato da diretora',
            'diretor',
            'diretora',
            'documentos para matricula',
            'documentos para matrícula',
            'documentos exigidos para matricula',
            'documentos exigidos para matrícula',
        }
    )


def _is_public_pricing_context_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    active_task = _recent_slot_value(conversation_context, 'active_task')
    if active_task != 'public:pricing':
        return False
    return _should_reuse_public_pricing_slots(message)


def _is_public_curriculum_context_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    active_task = _recent_slot_value(conversation_context, 'active_task')
    if active_task != 'public:curriculum':
        return False
    normalized = _normalize_text(message)
    if _extract_public_curriculum_subject_focus(message) is not None:
        return True
    return bool(
        _is_follow_up_query(message)
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'outras materias',
                'outras matérias',
                'outras disciplinas',
                'quais materias',
                'quais matérias',
                'quais disciplinas',
                'que materias',
                'que matérias',
                'que disciplinas',
            }
        )
    )


def _is_service_routing_query(message: str) -> bool:
    normalized = _normalize_text(message)
    normalized_simple = normalized.strip(' ?.!')
    if normalized_simple in {'com quem eu falo', 'pra quem eu falo', 'para quem eu falo'}:
        return False
    return any(_message_matches_term(normalized, term) for term in SERVICE_ROUTING_TERMS)


def _is_direct_service_routing_bundle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not _is_service_routing_query(message):
        return False
    sector_hits = sum(
        1
        for term in (
            'bolsa',
            'bolsas',
            'financeiro',
            'direcao',
            'direção',
            'secretaria',
            'admissoes',
            'admissões',
            'coordenacao',
            'coordenação',
            'orientacao',
            'orientação',
        )
        if _message_matches_term(normalized, term)
    )
    if sector_hits < 2:
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in (
            'mensalidade',
            'matricula',
            'matrícula',
            'valor',
            'quanto',
            'preco',
            'preço',
            'calendario',
            'calendário',
            'marco',
            'marcos',
            'etapa',
            'etapas',
            'timeline',
            'protocolo formal',
        )
    ):
        return False
    return True


def _map_request(
    request: MessageResponseRequest, user_context: UserContext
) -> OrchestrationRequest:
    return OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=user_context,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )


def _parse_csv_slices(value: str | None) -> list[str]:
    return [item.strip() for item in str(value or '').split(',') if item.strip()]


def _build_preview_state_input(
    *,
    request: MessageResponseRequest,
    user_context: UserContext,
    settings: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        'request': _map_request(request, user_context),
    }
    if bool(getattr(settings, 'langgraph_hitl_user_traffic_enabled', False)):
        payload['hitl_enabled'] = True
        payload['hitl_target_slices'] = _parse_csv_slices(
            getattr(settings, 'langgraph_hitl_user_traffic_slices', 'support')
        )
    return payload


def _build_langgraph_pending_review_message(*, preview: Any) -> str:
    if preview.classification.domain is QueryDomain.support:
        return (
            'Seu pedido entrou em revisao humana antes da proxima etapa para manter o atendimento seguro e rastreavel. '
            'Assim que a equipe validar esse ponto, eu sigo desta mesma conversa.'
        )
    if preview.classification.access_tier is not AccessTier.public:
        return (
            'Essa consulta ficou pendente de revisao antes da liberacao final, para proteger os dados da conta e manter a trilha auditavel. '
            'Assim que esse ponto for validado, eu continuo daqui.'
        )
    return (
        'Esse pedido ficou pendente de revisao antes da resposta final. '
        'Assim que a validacao for concluida, eu continuo desta mesma conversa.'
    )


def _effective_conversation_id(request: MessageResponseRequest) -> str | None:
    if request.conversation_id:
        return request.conversation_id
    if request.channel.value == 'telegram' and request.telegram_chat_id is not None:
        return f'telegram:{request.telegram_chat_id}'
    return None


def _category_for_domain(domain: QueryDomain) -> str | None:
    if domain is QueryDomain.calendar:
        return 'calendar'
    return None


def _collect_citations(hits: list[Any], limit: int = 3) -> list[MessageResponseCitation]:
    citations: list[MessageResponseCitation] = []
    seen: set[tuple[str, str]] = set()
    for hit in hits:
        document_key = (hit.citation.document_title, hit.citation.version_label)
        if document_key in seen:
            continue
        citations.append(
            MessageResponseCitation(
                document_title=hit.citation.document_title,
                version_label=hit.citation.version_label,
                storage_path=hit.citation.storage_path,
                chunk_id=hit.citation.chunk_id,
                excerpt=hit.text_excerpt,
            )
        )
        seen.add(document_key)
        if len(citations) >= limit:
            break
    return citations


def _render_source_lines(citations: list[MessageResponseCitation]) -> str:
    if not citations:
        return ''
    lines = ['Fontes:']
    for citation in citations:
        lines.append(f'- {citation.document_title} ({citation.version_label})')
    return '\n'.join(lines)


def _format_event_line(event: CalendarEventCard) -> str:
    start = event.starts_at.astimezone().strftime('%d/%m/%Y %H:%M')
    end = event.ends_at.astimezone().strftime('%d/%m/%Y %H:%M')
    if event.description:
        return f'- {start} a {end}: {event.title}. {event.description}'
    return f'- {start} a {end}: {event.title}'


def _contains_any(message: str, terms: set[str]) -> bool:
    lowered = _normalize_text(message)
    return any(_message_matches_term(lowered, term) for term in terms)


def _message_matches_term(message: str, term: str) -> bool:
    normalized_term = _normalize_text(term).strip()
    if not normalized_term:
        return False
    pattern = (
        r'(?<!\w)' + r'\s+'.join(re.escape(part) for part in normalized_term.split()) + r'(?!\w)'
    )
    return re.search(pattern, message) is not None


def _extract_public_entity_hints(message: str) -> set[str]:
    lowered = _normalize_text(message)
    return {
        canonical
        for term, canonical in PUBLIC_ENTITY_HINTS.items()
        if _message_matches_term(lowered, term)
    }


def _primary_public_entity_hint(
    message: str, conversation_context: dict[str, Any] | None = None
) -> str | None:
    hints = sorted(_extract_public_entity_hints(message))
    if hints:
        return hints[0]
    return _recent_slot_value(conversation_context, 'public_entity')


def _should_reuse_public_context(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
) -> bool:
    if _is_follow_up_query(message):
        return True
    return bool(public_plan and public_plan.use_conversation_context)


def _should_track_contact_subject(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    recent_focus: dict[str, Any],
) -> bool:
    if _requested_contact_channel(message) is not None or _contact_is_general_school_query(message):
        return True
    if public_plan is not None and public_plan.conversation_act in {
        'contacts',
        'service_routing',
        'document_submission',
        'careers',
        'teacher_directory',
        'leadership',
    }:
        return True
    return str(recent_focus.get('active_task', '') or '').strip() in {
        'public:contacts',
        'public:service_routing',
    }


def _should_track_feature_key(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    recent_focus: dict[str, Any],
) -> bool:
    if public_plan is not None and public_plan.conversation_act == 'features':
        return True
    if not _is_follow_up_query(message):
        return False
    return str(recent_focus.get('active_task', '') or '').strip() == 'public:features'


def _requested_operating_hours_attribute(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {'fecha', 'fechar', 'fechamento', 'encerra', 'encerramento'}
    ):
        return 'close_time'
    if any(
        _message_matches_term(normalized, term)
        for term in {'abre', 'abertura', 'abre as', 'abre às'}
    ):
        return 'open_time'
    recent_attribute = _recent_slot_value(conversation_context, 'public_attribute')
    if recent_attribute in {'open_time', 'close_time'} and _is_follow_up_query(message):
        return recent_attribute
    return None


def _detect_admin_attribute_request(
    message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_text(message)
    academic_progression_query = _looks_like_academic_progression_query(
        message,
        conversation_context=conversation_context,
    )
    academic_attribute_request = _detect_academic_attribute_request(message)
    if (
        _wants_academic_grade_requirement(message)
        or academic_progression_query
        or (
            academic_attribute_request is not None
            and str(getattr(academic_attribute_request, 'domain', '') or '').strip() == 'academic'
        )
    ):
        return None
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'proximo passo',
            'próximo passo',
            'o que falta',
            'qual o proximo passo',
            'agir em seguida',
            'como agir em seguida',
            'o que fazer em seguida',
        }
    ):
        return 'next_step'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'pendencia documental',
            'pendência documental',
            'pendencias documentais',
            'pendências documentais',
            'acao recomendada',
            'ação recomendada',
            'proximo passo recomendado',
            'próximo passo recomendado',
        }
    ):
        return 'documents'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'pendencia',
            'pendência',
            'pendencias',
            'pendências',
            'regularizar',
            'bloqueando atendimento',
            'bloqueio',
        }
    ) and any(
        _message_matches_term(normalized, term)
        for term in {
            'cadastro',
            'responsavel',
            'responsável',
            'documentacao',
            'documentação',
            'administrativo',
            'administrativa',
        }
    ):
        return 'documents'
    if any(
        _message_matches_term(normalized, term)
        for term in {'status', 'situacao', 'situação', 'como esta'}
    ):
        return 'status'
    if any(
        _message_matches_term(normalized, term)
        for term in {'parte administrativa', 'situacao administrativa', 'situação administrativa'}
    ):
        return 'documents'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'documentos',
            'documentacao',
            'documentação',
            'documental',
            'documentais',
            'comprovante',
            'comprovantes',
        }
    ):
        return 'documents'
    if any(_message_matches_term(normalized, term) for term in {'telefone', 'celular', 'fone'}):
        return 'phone'
    if any(_message_matches_term(normalized, term) for term in {'email', 'e-mail', 'mail'}):
        return 'email'
    recent_attribute = _recent_slot_value(conversation_context, 'admin_attribute')
    if recent_attribute and _is_follow_up_query(message):
        return recent_attribute
    return None


def _derive_public_active_task(public_plan: PublicInstitutionPlan | None) -> str | None:
    if public_plan is None:
        return None
    return PUBLIC_ACTIVE_TASK_BY_ACT.get(
        public_plan.conversation_act, f'public:{public_plan.conversation_act}'
    )


def _derive_public_active_entity(
    *,
    public_plan: PublicInstitutionPlan | None,
    public_entity: str | None,
    contact_subject: str | None,
    feature_key: str | None,
    current_message: str,
    time_reference: str | None,
) -> str | None:
    if public_plan is None:
        return None
    if public_plan.conversation_act == 'features':
        requested_features = _requested_public_features(current_message)
        if feature_key:
            return feature_key.replace('_', ' ')
        if len(requested_features) > 1:
            return 'escola'
    if public_entity:
        return public_entity
    if public_plan.conversation_act == 'contacts' and contact_subject:
        return contact_subject.lower()
    if public_plan.conversation_act == 'operating_hours' and _message_matches_term(
        _normalize_text(current_message), 'biblioteca'
    ):
        return 'biblioteca'
    if public_plan.conversation_act == 'timeline' and time_reference:
        return time_reference
    return PUBLIC_ACTIVE_ENTITY_BY_ACT.get(public_plan.conversation_act)


def _derive_active_task(
    *,
    current_message: str,
    public_plan: PublicInstitutionPlan | None,
    focus_kind: str | None,
    academic_focus_kind: str | None,
    academic_student_name: str | None,
    finance_student_name: str | None,
    finance_attribute: str | None,
    finance_action: str | None,
    preview: Any | None,
) -> str | None:
    public_task = _derive_public_active_task(public_plan)
    if public_task:
        return public_task
    if preview is not None and getattr(preview, 'classification', None) is not None:
        domain = getattr(preview.classification, 'domain', None)
        selected_tool_names = {
            str(tool_name).strip()
            for tool_name in getattr(preview, 'selected_tools', [])
            if isinstance(tool_name, str)
        }
        if domain is QueryDomain.institution and 'get_administrative_status' in selected_tool_names:
            if 'get_student_administrative_status' in selected_tool_names and (
                academic_student_name or finance_student_name
            ):
                return 'admin:student_administrative_status'
            if _wants_profile_update_guidance(current_message):
                return 'admin:profile_update'
            return 'admin:administrative_status'
        if (
            domain is QueryDomain.institution
            and 'get_actor_identity_context' in selected_tool_names
        ):
            normalized_current = _normalize_text(current_message)
            if _is_access_scope_query(current_message):
                return 'admin:access_scope'
            if any(
                _message_matches_term(normalized_current, term)
                for term in {
                    'quais meus filhos',
                    'quais sao meus filhos',
                    'quais são meus filhos',
                    'quem sao meus filhos',
                    'quem são meus filhos',
                    'quais filhos tenho',
                    'filhos matriculados',
                    'filhos vinculados',
                    'alunos vinculados',
                }
            ):
                return 'admin:linked_students'
            return 'admin:actor_identity'
        if domain is QueryDomain.academic:
            return ACADEMIC_ACTIVE_TASK_BY_FOCUS.get(
                academic_focus_kind or '', 'academic:student_summary'
            )
        if domain is QueryDomain.finance:
            if finance_action == 'second_copy':
                return 'finance:second_copy'
            if finance_attribute:
                return f'finance:{finance_attribute}'
            return 'finance:billing'
    if focus_kind:
        return WORKFLOW_ACTIVE_TASK_BY_KIND.get(focus_kind)
    return None


def _derive_active_entity(
    *,
    active_task: str | None,
    focus_kind: str | None,
    public_plan: PublicInstitutionPlan | None,
    public_entity: str | None,
    contact_subject: str | None,
    feature_key: str | None,
    current_message: str,
    time_reference: str | None,
    academic_student_name: str | None,
    finance_student_name: str | None,
) -> str | None:
    if active_task == 'admin:actor_identity':
        return 'sua conta'
    if active_task == 'admin:access_scope':
        return 'sua conta'
    if active_task == 'admin:linked_students':
        return 'seus alunos vinculados'
    if active_task and active_task.startswith('admin:'):
        if active_task == 'admin:student_administrative_status':
            return academic_student_name or finance_student_name or 'aluno'
        return 'seu cadastro'
    if active_task and active_task.startswith('academic:'):
        return academic_student_name or 'aluno'
    if active_task and active_task.startswith('finance:'):
        return finance_student_name or 'responsavel financeiro'
    public_entity_value = _derive_public_active_entity(
        public_plan=public_plan,
        public_entity=public_entity,
        contact_subject=contact_subject,
        feature_key=feature_key,
        current_message=current_message,
        time_reference=time_reference,
    )
    if public_entity_value:
        return public_entity_value
    if focus_kind:
        return WORKFLOW_ACTIVE_ENTITY_BY_KIND.get(focus_kind)
    return None


def _derive_pending_question_type(
    *,
    message: str,
    public_plan: PublicInstitutionPlan | None,
    public_attribute: str | None,
    requested_channel: str | None,
    academic_attribute: str | None,
    admin_attribute: str | None,
    finance_attribute: str | None,
    finance_action: str | None,
    time_reference: str | None,
    focus_kind: str | None,
) -> str | None:
    if public_plan is not None and public_plan.secondary_acts:
        return 'multi_intent'
    if _is_follow_up_query(message):
        return 'follow_up'
    if any(
        value
        for value in (
            public_attribute,
            requested_channel,
            academic_attribute,
            admin_attribute,
            finance_attribute,
            finance_action,
        )
    ):
        return 'attribute_query'
    if time_reference:
        return 'time_query'
    if focus_kind in {'visit', 'request'}:
        return 'workflow_query'
    return None


def _follow_up_context_phrase(active_task: str | None, active_entity: str | None) -> str | None:
    if not active_task:
        return None
    template = FOLLOW_UP_CONTEXT_BY_TASK.get(active_task)
    if not template:
        return None
    entity = (active_entity or 'esse assunto').strip()
    return template.format(entity=entity)


def _is_prompt_disclosure_probe(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in PROMPT_DISCLOSURE_TERMS) or any(
        term in normalized for term in PROMPT_BYPASS_TERMS
    )


def _is_negative_requirement_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_negative = any(
        _message_matches_term(normalized, term) for term in NEGATIVE_REQUIREMENT_TERMS
    )
    has_requirement = any(
        _message_matches_term(normalized, term) for term in REQUIREMENT_QUERY_TERMS
    )
    return has_negative and has_requirement


def _is_positive_requirement_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _is_negative_requirement_query(message):
        return False
    has_requirement = any(
        _message_matches_term(normalized, term) for term in REQUIREMENT_QUERY_TERMS
    )
    has_positive = any(
        _message_matches_term(normalized, term)
        for term in {
            'exigido',
            'exigidos',
            'exigida',
            'exigidas',
            'necessario',
            'necessarios',
            'preciso',
            'levar',
        }
    )
    return has_requirement and has_positive


def _is_comparative_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in COMPARATIVE_TERMS):
        return False
    return looks_like_school_domain_request(message)


def _is_follow_up_query(message: str) -> bool:
    raw = message.strip().lower()
    if raw.startswith('é ') or raw == 'é':
        return False
    normalized = _normalize_text(message).strip()
    if len(normalized) > 180:
        return False
    if any(normalized.startswith(opener) for opener in FOLLOW_UP_OPENERS):
        return True
    return any(_message_matches_term(normalized, term) for term in FOLLOW_UP_REFERENTS)


def _detect_time_reference(message: str) -> str | None:
    explicit_date = _extract_requested_date(message)
    if explicit_date is not None:
        return explicit_date.isoformat()
    normalized = _normalize_text(message)
    if _message_matches_term(normalized, 'amanha') or _message_matches_term(normalized, 'amanhã'):
        return 'tomorrow'
    if _message_matches_term(normalized, 'hoje'):
        return 'today'
    return None


def _detect_academic_attribute_request(message: str) -> ProtectedAttributeRequest | None:
    normalized = _normalize_text(message)
    if _looks_like_finance_open_amount_query(message):
        return None
    if any(_message_matches_term(normalized, term) for term in ACADEMIC_IDENTITY_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='enrollment_code')
    if any(_message_matches_term(normalized, term) for term in ATTENDANCE_TIMELINE_TERMS):
        return None
    if any(_message_matches_term(normalized, term) for term in UPCOMING_ASSESSMENT_TERMS):
        return None
    if _wants_academic_grade_requirement(message):
        return ProtectedAttributeRequest(domain='academic', attribute='grade_requirement')
    if (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'materia',
                'materias',
                'disciplina',
                'disciplinas',
                'componente',
                'componentes',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'fragilizada',
                'fragilizado',
                'mais fragilizada',
                'mais fragilizado',
                'mais exposta',
                'mais exposto',
                'vulneravel',
                'vulnerável',
                'mais vulneravel',
                'mais vulnerável',
            }
        )
    ) or any(
        _message_matches_term(normalized, term)
        for term in {
            'veredito academico',
            'veredito acadêmico',
            'quem esta mais perto de reprovar',
            'quem está mais perto de reprovar',
            'mais perto de reprovar',
            'mais proximo de reprovar',
            'mais próximo de reprovar',
            'risco de reprovacao',
            'risco de reprovação',
            'ponto academico mais fraco',
            'ponto acadêmico mais fraco',
            'ponto academico mais sensivel',
            'ponto acadêmico mais sensível',
            'fragilizada academicamente',
            'fragilizado academicamente',
            'mais fragilizada academicamente',
            'mais fragilizado academicamente',
            'mais exposta academicamente',
            'mais exposto academicamente',
        }
    ):
        return ProtectedAttributeRequest(domain='academic', attribute='grades')
    if _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='attendance')
    if _contains_any(message, GRADE_TERMS):
        return ProtectedAttributeRequest(domain='academic', attribute='grades')
    return None


def _detect_finance_attribute_request(message: str) -> ProtectedAttributeRequest | None:
    normalized = _normalize_text(message)
    if _looks_like_finance_open_amount_query(message):
        return ProtectedAttributeRequest(domain='finance', attribute='open_amount')
    wants_open_amount = any(
        _message_matches_term(normalized, term)
        for term in {
            'quanto esta em aberto',
            'quanto está em aberto',
            'valor em aberto',
            'saldo em aberto',
            'quanto devo',
            'quanto estou devendo',
            'valor pendente',
        }
    ) or (
        any(_message_matches_term(normalized, term) for term in FINANCE_OPEN_TERMS)
        and any(
            _message_matches_term(normalized, term)
            for term in {'quanto', 'valor', 'saldo', 'devo', 'devendo'}
        )
    )
    if wants_open_amount:
        return ProtectedAttributeRequest(domain='finance', attribute='open_amount')
    if any(_message_matches_term(normalized, term) for term in FINANCE_NEXT_DUE_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='next_due')
    if any(_message_matches_term(normalized, term) for term in FINANCE_IDENTIFIER_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='invoice_id')
    if any(_message_matches_term(normalized, term) for term in FINANCE_CONTRACT_TERMS):
        return ProtectedAttributeRequest(domain='finance', attribute='contract_code')
    return None


def _wants_finance_second_copy(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in FINANCE_SECOND_COPY_TERMS):
        return True
    recent_second_copy = _recent_slot_value(conversation_context, 'finance_action') == 'second_copy'
    if not recent_second_copy:
        return False
    if _is_follow_up_query(message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in FINANCE_IDENTIFIER_TERMS | {'boleto', 'fatura'}
    ):
        return True
    return False


def _effective_finance_status_filter(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> set[str] | None:
    explicit = _detect_finance_status_filter(message)
    if explicit is not None:
        return explicit
    if not _is_follow_up_query(message):
        return None
    raw = _recent_slot_value(conversation_context, 'finance_status_filter')
    if not raw:
        return None
    values = {part.strip() for part in raw.split(',') if part.strip()}
    return values or None


def _effective_finance_attribute_request(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> ProtectedAttributeRequest | None:
    explicit = _detect_finance_attribute_request(message)
    if explicit is not None:
        return explicit
    if not _is_follow_up_query(message):
        return None
    raw = _recent_slot_value(conversation_context, 'finance_attribute')
    if raw:
        return ProtectedAttributeRequest(domain='finance', attribute=raw)
    return None


def _effective_academic_attribute_request(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> ProtectedAttributeRequest | None:
    explicit = _detect_academic_attribute_request(message)
    if explicit is not None:
        recent_focus_kind = str(
            _recent_slot_value(conversation_context, 'academic_focus_kind') or ''
        ).strip()
        recent_active_task = str(
            _recent_slot_value(conversation_context, 'active_task') or ''
        ).strip()
        if (
            explicit.attribute == 'subject'
            and recent_focus_kind == 'upcoming'
            and (recent_active_task == 'academic:upcoming' or _is_follow_up_query(message))
        ):
            return None
        return explicit
    if _looks_like_academic_difficulty_query(message, conversation_context=conversation_context):
        return None
    if _wants_upcoming_assessments(message) or _wants_attendance_timeline(message):
        return None
    if not _should_inherit_academic_attribute_from_context(
        message,
        conversation_context=conversation_context,
    ):
        return None
    raw = _recent_slot_value(conversation_context, 'academic_attribute')
    if raw:
        return ProtectedAttributeRequest(domain='academic', attribute=raw)
    return None


def _wants_academic_grade_requirement(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in GRADE_REQUIREMENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'quanto falta', 'falta quanto'}):
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'fechar a media',
                'fechar a média',
                'atingir a media',
                'atingir a média',
                'bater a media',
                'bater a média',
            }
        ):
            return bool(_subject_reference_tokens(normalized)) or _contains_any(normalized, GRADE_TERMS)
        return any(_message_matches_term(normalized, term) for term in GRADE_APPROVAL_TERMS)
    if any(_message_matches_term(normalized, term) for term in GRADE_APPROVAL_TERMS):
        return bool(_subject_reference_tokens(normalized)) or _contains_any(normalized, GRADE_TERMS)
    return False


def _subject_reference_tokens(text: str) -> set[str]:
    normalized = _normalize_text(text)
    return {
        token
        for token in {
            'fisica',
            'matematica',
            'biologia',
            'filosofia',
            'geografia',
            'historia',
            'quimica',
            'portugues',
            'educacao fisica',
            'ingles',
        }
        if token in normalized
    }


def _compose_negative_requirement_answer() -> str:
    lines = [
        'A base atual informa os documentos exigidos para a matricula, mas nao lista explicitamente quais documentos sao dispensaveis.',
        'Por isso, nao e seguro afirmar o que voce "nao precisa" levar.',
        'O que esta explicitamente exigido hoje e:',
    ]
    lines.extend(f'- {item}' for item in KNOWN_ADMISSIONS_REQUIREMENTS)
    lines.append(
        'Se quiser, eu posso resumir apenas os documentos exigidos ou explicar as etapas da matricula.'
    )
    return '\n'.join(lines)


def _compose_required_documents_answer(profile: dict[str, Any] | None = None) -> str:
    requirements: list[str] = []
    if isinstance(profile, dict):
        requirements = [
            str(item).strip()
            for item in (profile.get('admissions_required_documents') or [])
            if isinstance(item, str) and str(item).strip()
        ]
    requirements = requirements or list(KNOWN_ADMISSIONS_REQUIREMENTS)
    lines = ['Hoje os documentos exigidos para a matricula publicados pela escola sao:']
    lines.extend(f'- {item}' for item in requirements)
    lines.append(
        'Se quiser, eu tambem posso explicar as etapas da matricula ou como funciona o envio inicial desses documentos.'
    )
    return '\n'.join(lines)


def _compose_comparative_gap_answer(profile: dict[str, Any] | None = None) -> str:
    return _compose_public_comparative_answer(profile or {})


def _extract_salient_terms(message: str) -> set[str]:
    normalized = _normalize_text(message)
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in QUERY_STOPWORDS and not token.isdigit()
    }
    if 'matricula' in normalized:
        tokens.add('matricula')
    if 'biblioteca' in normalized:
        tokens.add('biblioteca')
    return tokens


def _extract_public_gap_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    if _message_matches_term(normalized, 'confessional'):
        return 'se a escola e confessional'

    facility_labels: list[str] = []
    has_tennis_court = _message_matches_term(normalized, 'quadra de tenis')
    for term, label in [
        ('academia', 'academia'),
        ('piscina', 'piscina'),
        ('quadra de tenis', 'quadra de tenis'),
        ('quadra', 'quadra'),
        ('tenis', 'tenis'),
        ('futebol', 'futebol'),
        ('danca', 'aulas de danca'),
        ('dança', 'aulas de danca'),
    ]:
        if has_tennis_court and term in {'quadra', 'tenis'}:
            continue
        if _message_matches_term(normalized, term) and label not in facility_labels:
            facility_labels.append(label)

    if facility_labels:
        if len(facility_labels) == 1:
            return f'se a escola possui {facility_labels[0]}'
        if len(facility_labels) == 2:
            return f'se a escola possui {facility_labels[0]} e {facility_labels[1]}'
        return f'se a escola possui {", ".join(facility_labels[:-1])} e {facility_labels[-1]}'

    return None


def _contains_high_risk_reasoning(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, phrase) for phrase in HIGH_RISK_REASONING_PHRASES):
        return True
    return any(_message_matches_term(normalized, term) for term in HIGH_RISK_REASONING_TERMS)


def _extract_admissions_requirement_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    for term, label in ADMISSIONS_REQUIREMENT_FOCUS.items():
        if _message_matches_term(normalized, term):
            return label
    return None


def _assess_public_answerability(
    message: str, retrieval_hits: list[Any], query_hints: set[str]
) -> PublicAnswerabilityAssessment:
    salient_terms = _extract_salient_terms(message)
    if query_hints:
        salient_terms = {*(salient_terms), *query_hints}
    if not salient_terms:
        return PublicAnswerabilityAssessment(
            enough_support=bool(retrieval_hits),
            salient_terms=set(),
            matched_terms=set(),
            unsupported_terms=set(),
            coverage_ratio=1.0 if retrieval_hits else 0.0,
            high_risk_reasoning=_contains_high_risk_reasoning(message),
        )

    haystack = ' '.join(
        _normalize_text(
            ' '.join(
                filter(
                    None,
                    [
                        getattr(hit, 'document_title', None),
                        getattr(hit, 'text_excerpt', None),
                        getattr(hit, 'contextual_summary', None),
                    ],
                )
            )
        )
        for hit in retrieval_hits
    )
    matched_terms = {term for term in salient_terms if term in haystack}
    unsupported_terms = salient_terms - matched_terms
    coverage_ratio = len(matched_terms) / len(salient_terms) if salient_terms else 0.0
    high_risk_reasoning = _contains_high_risk_reasoning(message)
    enough_support = bool(retrieval_hits) and coverage_ratio >= (
        0.75 if high_risk_reasoning else 0.45
    )
    if high_risk_reasoning and unsupported_terms:
        enough_support = False
    return PublicAnswerabilityAssessment(
        enough_support=enough_support,
        salient_terms=salient_terms,
        matched_terms=matched_terms,
        unsupported_terms=unsupported_terms,
        coverage_ratio=coverage_ratio,
        high_risk_reasoning=high_risk_reasoning,
    )


def _compose_answerability_gap_answer(
    assessment: PublicAnswerabilityAssessment, message: str
) -> str:
    requirement_focus = _extract_admissions_requirement_focus(message)
    if assessment.high_risk_reasoning:
        if requirement_focus and _contains_any(
            message,
            {'excecao', 'dispensa', 'dispensavel', 'dispensaveis', 'nao preciso', 'nao precisa'},
        ):
            return (
                f'A base publica atual registra {requirement_focus} como requisito da matricula, '
                'mas nao descreve excecoes, dispensas ou condicoes especiais para esse item. '
                'Para evitar uma orientacao incorreta, nao vou afirmar que exista uma excecao sem documento oficial especifico. '
                'Se quiser, eu posso resumir apenas os requisitos explicitamente publicados.'
            )
        if assessment.unsupported_terms:
            labels = ', '.join(sorted(assessment.unsupported_terms))
            return (
                'A base publica atual nao sustenta com seguranca todos os pontos dessa pergunta, '
                f'especialmente sobre: {labels}. '
                'Para evitar uma orientacao incorreta, prefiro nao inferir alem do que esta documentado. '
                'Se quiser, eu posso responder apenas o que esta explicitamente registrado na base atual.'
            )
        return (
            'A pergunta exige uma regra, excecao ou condicao que nao esta suficientemente sustentada '
            'pela base publica atual. Posso responder apenas o que estiver explicitamente documentado.'
        )
    return _compose_public_gap_answer(assessment.unsupported_terms, message)


def _compose_public_gap_answer(query_hints: set[str], message: str | None = None) -> str:
    normalized_message = _normalize_text(message or '')
    if message and _is_public_document_submission_query(message):
        if _message_matches_term(normalized_message, 'fax'):
            return (
                'Hoje a escola nao utiliza fax para envio de documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'telegrama'):
            return (
                'Hoje a escola nao publica telegrama como canal valido para documentos. '
                'Para isso, use portal institucional, email da secretaria, secretaria presencial.'
            )
        if _message_matches_term(normalized_message, 'caixa postal'):
            return (
                'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
                'Para documentos, use portal institucional, email da secretaria, secretaria presencial.'
            )
        return 'Para enviar documentos hoje, use portal institucional, email da secretaria ou secretaria presencial.'
    if any(
        _message_matches_term(normalized_message, term)
        for term in {'abre pra', 'abre para', 'encaminha pra', 'encaminha para'}
    ):
        queue_label = None
        if any(_message_matches_term(normalized_message, term) for term in {'secretaria'}):
            queue_label = 'secretaria'
        elif any(_message_matches_term(normalized_message, term) for term in {'financeiro'}):
            queue_label = 'financeiro'
        elif any(
            _message_matches_term(normalized_message, term) for term in {'direcao', 'direção'}
        ):
            queue_label = 'direcao'
        elif any(
            _message_matches_term(normalized_message, term)
            for term in {'coordenacao', 'coordenação'}
        ):
            queue_label = 'coordenacao'
        if queue_label:
            return (
                f'Sem problema, sigo daqui com atendimento humano para {queue_label}. '
                'Se quiser, eu tambem posso resumir o assunto em uma frase para deixar esse encaminhamento mais claro.'
            )
    focus = _extract_public_gap_focus(message or '')
    if focus:
        return (
            f'Hoje eu nao encontrei uma informacao publica oficial sobre {focus}. '
            'Se isso for decisivo para voce, a escola precisa publicar esse ponto de forma oficial ou ampliar a base documental.'
        )
    if query_hints:
        return (
            'Ainda nao encontrei evidencia publica suficiente para responder isso com seguranca do jeito que a pergunta foi feita. '
            'Se quiser, eu posso tentar por outro caminho, como o setor responsavel, o canal oficial ou a politica institucional relacionada.'
        )
    return (
        'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
        'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
    )
