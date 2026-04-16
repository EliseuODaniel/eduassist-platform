from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Deterministic and supplemental helpers extracted from grounded_answer_experience.py."""

LOCAL_EXTRACTED_NAMES = {'_deterministic_public_direct_answer', '_deterministic_protected_academic_direct_answer', '_deterministic_protected_attendance_direct_answer', '_deterministic_protected_finance_direct_answer', '_build_supplemental_focus', '_preserve_deterministic_answer_surface'}

from . import grounded_answer_experience as _native

def _refresh_native_namespace() -> None:
    for name, value in vars(_native).items():
        if name.startswith('__') or name in LOCAL_EXTRACTED_NAMES:
            continue
        globals()[name] = value


def _reason_has_marker(reason: str | None, markers: tuple[str, ...]) -> bool:
    normalized = _normalize_text(reason)
    if not normalized:
        return False
    return any(marker in normalized for marker in markers)


def _is_boundary_answer_surface(*reasons: str | None) -> bool:
    markers = (
        'external_public_facility_boundary',
        'scope_boundary',
        'deterministic_public_guardrail',
        'deterministic_scope_boundary',
        'out_of_scope_abstention',
        'contextual_boundary_fast_path',
        'contextual_boundary',
    )
    return any(_reason_has_marker(reason, markers) for reason in reasons)


def _is_restricted_document_surface(*reasons: str | None) -> bool:
    markers = (
        'restricted_document_no_match',
        'restricted_doc_no_match',
        'restricted_access_denied',
        'restricted_doc_access_deny',
    )
    return any(_reason_has_marker(reason, markers) for reason in reasons)


def _wants_upcoming_assessments(message: str) -> bool:
    from .intent_analysis_runtime import _wants_upcoming_assessments as _impl

    return _impl(message)


def _looks_like_external_public_facility_boundary(message: str) -> bool:
    from .kernel_runtime import _message_mentions_external_library_entity as _impl

    return _impl(message)


def _compose_external_public_facility_boundary_answer(
    profile: dict[str, Any],
    *,
    facility_label: str,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    from .public_profile_runtime import _compose_external_public_facility_boundary_answer as _impl

    return _impl(
        profile,
        facility_label=facility_label,
        conversation_context=conversation_context,
    )


def _compose_admin_finance_combined_answer_local(
    *,
    admin_summary: dict[str, Any] | None,
    finance_summaries: list[dict[str, Any]],
    requested_admin_attribute: str | None,
) -> str | None:
    from .protected_summary_runtime import _compose_admin_finance_combined_answer as _impl

    return _impl(
        admin_summary=admin_summary,
        finance_summaries=finance_summaries,
        requested_admin_attribute=requested_admin_attribute,
    )


def _is_admin_finance_combined_query_local(message: str) -> bool:
    from .intent_analysis_runtime import _is_admin_finance_combined_query as _impl

    return _impl(message)


def _resolve_linked_student_candidate(
    *,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    allow_recent_context: bool = False,
    focus: AnswerFocusState | None = None,
    focused_student: dict[str, Any] | None = None,
    mentioned_students: list[str] | None = None,
) -> dict[str, Any] | None:
    if isinstance(focused_student, dict):
        return focused_student
    if not isinstance(actor, dict):
        return None
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list) or not linked_students:
        return None

    focus_student_id = str(getattr(focus, 'student_id', '') or '').strip() if focus is not None else ''
    if focus_student_id:
        for student in linked_students:
            if isinstance(student, dict) and str(student.get('student_id') or '').strip() == focus_student_id:
                return student

    focus_student_name = str(getattr(focus, 'student_name', '') or '').strip() if focus is not None else ''
    mentioned_names = [
        _plain_text(name)
        for name in (mentioned_students or [])
        if str(name or '').strip()
    ]
    requested_names = [name for name in [focus_student_name] if name]
    requested_names.extend(name for name in mentioned_names if name)
    if requested_names:
        for requested_name in requested_names:
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                full_name = str(student.get('full_name') or '').strip()
                full_name_plain = _plain_text(full_name)
                first_name_plain = full_name_plain.split(' ')[0] if full_name_plain else ''
                if requested_name == full_name_plain or requested_name == first_name_plain:
                    return student

    if len(linked_students) == 1 and isinstance(linked_students[0], dict):
        return linked_students[0]

    if allow_recent_context:
        recent_student_name = _recent_linked_student_name_from_messages(conversation_context, actor) or _recent_linked_student_name_for_admin_finance_combo(
            conversation_context,
            actor,
        )
        recent_student_name_plain = _plain_text(recent_student_name)
        if recent_student_name_plain:
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                full_name = str(student.get('full_name') or '').strip()
                full_name_plain = _plain_text(full_name)
                first_name_plain = full_name_plain.split(' ')[0] if full_name_plain else ''
                if recent_student_name_plain == full_name_plain or recent_student_name_plain == first_name_plain:
                    return student
    return None

async def _deterministic_public_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    school_profile: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    _refresh_native_namespace()
    response_reason = _normalize_text(getattr(response, 'reason', None))
    candidate_reason = _normalize_text(getattr(response, 'candidate_reason', None))
    if _is_boundary_answer_surface(response_reason, candidate_reason) or _is_restricted_document_surface(
        response_reason,
        candidate_reason,
    ):
        return None
    if _looks_like_external_public_facility_boundary(request.message):
        return _compose_external_public_facility_boundary_answer(
            school_profile or {},
            facility_label='uma biblioteca publica externa',
            conversation_context=conversation_context,
        )
    canonical_lane = (
        match_shared_public_canonical_lane(request.message)
        or match_python_functions_public_canonical_lane(request.message)
    )
    if response.classification.access_tier is not AccessTier.public and (
        _looks_like_family_finance_aggregate_request(request.message)
        or _looks_like_access_scope_request(request.message)
    ):
        return None
    if response.classification.access_tier is not AccessTier.public and (
        _looks_like_attendance_alert_request(request.message)
        or _looks_like_family_attendance_aggregate_request(request.message)
    ):
        return None
    if _recent_family_attendance_context(conversation_context) and any(
        term in _plain_text(request.message)
        for term in (
            'corta para ',
            'fica so com ',
            'fique so com ',
            'fique só com ',
            'mantendo o contexto',
            'mantem o contexto',
            'mantém o contexto',
            'frequencia dele',
            'frequência dele',
            'risco mais concreto',
            'risco concreto',
        )
    ):
        return None
    teacher_directory = _question_mentions_public_teacher_directory(
        request.message,
        conversation_context=conversation_context,
    )
    permanence_support = _question_mentions_public_permanence_support(request.message)
    first_month_risks = _question_mentions_public_first_month_risks(request.message)
    visibility_boundary = _question_mentions_public_visibility_boundary(request.message)
    bolsas_and_processes = _question_mentions_public_bolsas_and_processes(request.message)
    health_emergency_bundle = _question_mentions_public_health_emergency_bundle(request.message)
    outings_authorizations = _question_mentions_public_outings_authorizations(request.message)
    known_unknown_key = detect_public_known_unknown_key(request.message)
    capabilities_query = _question_mentions_public_capabilities(request.message)
    website_query = _question_mentions_public_website(request.message)
    district_query = _question_mentions_public_district(request.message)
    bncc_query = _question_mentions_public_bncc(request.message)
    library_query = _question_mentions_public_library_identity(request.message)
    director_query = _question_mentions_public_director(request.message)
    admissions_opening_query = _question_mentions_public_admissions_opening(request.message)
    school_year_start_query = _question_mentions_public_school_year_start(request.message)
    family_meeting_query = _question_mentions_public_family_meeting(request.message)
    visit_reschedule_query = _question_mentions_visit_reschedule_followup(
        request.message,
        conversation_context,
    )
    visit_resume_query = _question_mentions_visit_resume_followup(
        request.message,
        conversation_context,
    )
    service_routing_bundle = _looks_like_service_routing_bundle_request(request.message)
    service_routing_followup = _looks_like_service_routing_followup(request.message, conversation_context)
    timeline_order_followup = _looks_like_public_timeline_order_followup(request.message, conversation_context)
    public_calendar_reset_followup = _looks_like_public_calendar_reset_followup(
        request.message,
        conversation_context,
    )
    outings_protocol_followup = _looks_like_public_outings_protocol_followup(
        request.message,
        conversation_context,
    )
    public_safe_direct_query = any(
        (
            canonical_lane in _PUBLIC_CANONICAL_SAFE_LANES,
            teacher_directory,
            permanence_support,
            first_month_risks,
            visibility_boundary,
            bolsas_and_processes,
            health_emergency_bundle,
            outings_authorizations,
            bool(known_unknown_key),
            capabilities_query,
            service_routing_bundle,
            service_routing_followup,
            timeline_order_followup,
            public_calendar_reset_followup,
            website_query,
            district_query,
            bncc_query,
            library_query,
            director_query,
            admissions_opening_query,
            school_year_start_query,
            family_meeting_query,
            visit_reschedule_query,
            visit_resume_query,
            outings_protocol_followup,
        )
    )
    if response.classification.access_tier is not AccessTier.public and not public_safe_direct_query:
        return None
    timeline_payload: dict[str, Any] | None = None
    capabilities_payload: dict[str, Any] | None = None
    if canonical_lane == 'public_bundle.conduct_frequency_punctuality':
        canonical_answer = compose_public_conduct_policy_contextual_answer(
            request.message,
            profile=school_profile,
        )
        if canonical_answer:
            return canonical_answer
    if teacher_directory:
        return compose_public_teacher_directory_boundary(school_profile)
    if visit_resume_query:
        return _compose_public_visit_resume_direct_answer(school_profile)
    if service_routing_bundle or service_routing_followup:
        direct_service_routing = _compose_public_service_routing_direct_answer(
            school_profile,
            message=request.message,
            conversation_context=conversation_context,
        )
        if direct_service_routing:
            return direct_service_routing
    if public_calendar_reset_followup:
        direct_public_calendar = compose_public_timeline_lifecycle_bundle()
        if direct_public_calendar:
            return direct_public_calendar
    if timeline_order_followup:
        timeline_payload = timeline_payload or await _fetch_public_timeline(settings)
        direct_timeline_order = _compose_public_timeline_order_direct_answer(
            school_profile,
            timeline_payload=timeline_payload,
        )
        if direct_timeline_order:
            return direct_timeline_order
    if canonical_lane in _PUBLIC_CANONICAL_SAFE_LANES:
        canonical_answer = compose_public_canonical_lane_answer(canonical_lane, profile=school_profile)
        if canonical_answer:
            return canonical_answer
    if permanence_support:
        return compose_public_permanence_and_family_support(school_profile)
    if first_month_risks:
        return compose_public_first_month_risks(school_profile)
    if visibility_boundary:
        return compose_public_calendar_visibility(school_profile)
    if bolsas_and_processes:
        return compose_public_bolsas_and_processes(school_profile)
    if health_emergency_bundle:
        return compose_public_health_emergency_bundle()
    if outings_authorizations:
        return compose_public_outings_authorizations()
    if known_unknown_key:
        return compose_public_known_unknown_answer(
            key=known_unknown_key,
            school_name=str((school_profile or {}).get('school_name') or 'Colegio Horizonte'),
        )
    if capabilities_query:
        capabilities_payload = await _fetch_public_assistant_capabilities(settings)
        return _compose_public_capabilities_direct_answer(school_profile, capabilities_payload)
    if website_query:
        website_url = str((school_profile or {}).get('website_url') or '').strip()
        school_name = str((school_profile or {}).get('school_name') or 'Colegio Horizonte').strip() or 'Colegio Horizonte'
        if website_url:
            return f'O site oficial de {school_name} hoje e {website_url}.'
        return (
            f'Hoje eu nao encontrei um site oficial publicado no perfil de {school_name}. '
            'Se quiser, eu posso te passar os canais institucionais de contato.'
        )
    if district_query:
        district = str((school_profile or {}).get('district') or '').strip()
        city = str((school_profile or {}).get('city') or '').strip()
        state = str((school_profile or {}).get('state') or '').strip()
        if district:
            suffix = f', {city}/{state}' if city and state else ''
            return f'A escola fica no bairro {district}{suffix}.'
    if bncc_query:
        curriculum_basis = str((school_profile or {}).get('curriculum_basis') or '').strip()
        if curriculum_basis:
            return f'Sim. No Ensino Medio, a base curricular publica da escola segue {curriculum_basis}'
    if library_query:
        inventory = (school_profile or {}).get('feature_inventory')
        if isinstance(inventory, list):
            for item in inventory:
                if not isinstance(item, dict):
                    continue
                feature_key = _plain_text(item.get('feature_key'))
                label = str(item.get('label') or item.get('name') or '').strip()
                notes = str(item.get('notes') or '').strip()
                if 'biblioteca' in feature_key or 'biblioteca' in _plain_text(label):
                    if label and notes:
                        return f'A biblioteca se chama {label} e funciona {notes}'
                    if label:
                        return f'A biblioteca se chama {label}.'
    if director_query:
        leadership = (school_profile or {}).get('leadership_team')
        if isinstance(leadership, list):
            for member in leadership:
                if not isinstance(member, dict):
                    continue
                title = str(member.get('title') or '').strip()
                if 'diretor' not in _plain_text(title) and 'direcao' not in _plain_text(title):
                    continue
                name = str(member.get('name') or '').strip()
                contact_channel = str(member.get('contact_channel') or '').strip()
                if name and contact_channel:
                    return f'{title}: {name}. Canal institucional: {contact_channel}.'
                if name:
                    return f'{title}: {name}.'
    if admissions_opening_query:
        timeline_payload = timeline_payload or await _fetch_public_timeline(settings)
        admissions_entry = _public_timeline_entry(
            school_profile,
            timeline_payload,
            topic_fragments=('admissions_opening', 'matricula'),
        )
        if isinstance(admissions_entry, dict):
            entry_date = _public_timeline_entry_date(admissions_entry)
            summary = str(admissions_entry.get('summary') or '').strip()
            if entry_date and summary:
                return f'No calendario publico atual, a matricula de 2026 abre em {entry_date}. {summary}'
            if summary:
                return summary
    if school_year_start_query:
        timeline_payload = timeline_payload or await _fetch_public_timeline(settings)
        school_year_entry = _public_timeline_entry(
            school_profile,
            timeline_payload,
            topic_fragments=('school_year_start', 'inicio das aulas', 'ano letivo'),
        )
        if isinstance(school_year_entry, dict):
            entry_date = _public_timeline_entry_date(school_year_entry)
            summary = str(school_year_entry.get('summary') or '').strip()
            if entry_date and summary:
                return f'No calendario publico atual, as aulas comecam em {entry_date}. {summary}'
            if summary:
                return summary
    if family_meeting_query:
        timeline_payload = timeline_payload or await _fetch_public_timeline(settings)
        family_entry = _public_timeline_entry(
            school_profile,
            timeline_payload,
            topic_fragments=('family_meeting', 'reuniao', 'responsaveis'),
        )
        if isinstance(family_entry, dict):
            entry_date = _public_timeline_entry_date(family_entry)
            summary = str(family_entry.get('summary') or '').strip()
            if entry_date and summary:
                return f'No calendario publico atual, a reuniao de pais acontece em {entry_date}. {summary}'
            if summary:
                return summary
    if visit_reschedule_query:
        return _compose_public_visit_reschedule_direct_answer(school_profile)
    if visit_resume_query:
        return _compose_public_visit_resume_direct_answer(school_profile)
    if outings_protocol_followup:
        if 'dois passos' in _plain_text(request.message):
            return _compose_public_outings_two_steps()
        return compose_public_outings_authorizations()
    return None


async def _deterministic_protected_academic_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    _refresh_native_namespace()
    if request.telegram_chat_id is None:
        return None
    if not isinstance(actor, dict):
        return None
    recent_family_academic = _recent_family_academic_context(conversation_context)
    recent_family_attendance = _recent_family_attendance_context(conversation_context)
    if response.classification.access_tier is AccessTier.public and not (recent_family_academic or recent_family_attendance):
        return None
    normalized = _plain_text(request.message)
    mentioned_students = _mentioned_linked_student_names_from_question(actor, request.message)
    focused_student = _focus_marked_student_from_question(actor, request.message)
    family_academic_priority_follow_up = _looks_like_family_academic_priority_followup(request.message)
    from .protected_summary_runtime import (
        _compose_academic_progression_answer as _compose_academic_progression_answer_local,
        _looks_like_academic_progression_query as _looks_like_academic_progression_query_local,
        _looks_like_family_academic_student_focus_followup,
    )

    family_student_focus_follow_up = _looks_like_family_academic_student_focus_followup(
        actor,
        request.message,
        conversation_context=conversation_context,
    )
    cross_student_comparison_follow_up = _looks_like_cross_student_academic_comparison_followup(request.message) or _looks_like_contextual_cross_student_academic_comparison_followup(
        request.message,
        conversation_context=conversation_context,
        mentioned_students=mentioned_students,
    )
    academic_risk_follow_up = any(
        term in normalized
        for term in (
            'risco academico',
            'risco acadêmico',
            'pontos academicos que mais preocupam',
            'pontos acadêmicos que mais preocupam',
            'pontos academicos',
            'pontos acadêmicos',
            'mais preocupam',
            'preocupacao academica',
            'preocupação acadêmica',
            'preocupacoes academicas',
            'preocupações acadêmicas',
            'componentes merecem mais atencao',
            'componentes merecem mais atenção',
            'componentes merecem acompanhamento',
            'componentes exigem mais atencao',
            'componentes exigem mais atenção',
            'qual componente',
            'qual disciplina',
            'mais alerta',
            'acende mais alerta',
            'fica mais claro',
        )
    )
    academic_difficulty_follow_up = any(
        term in normalized
        for term in (
            'mais dificil',
            'mais difícil',
            'menor media',
            'menor média',
            'piores medias',
            'piores médias',
        )
    )
    explicit_single_student_focus = isinstance(focused_student, dict) and any(
        term in normalized
        for term in (
            'qual componente',
            'qual disciplina',
            'mais alerta',
            'acende mais alerta',
            'chama mais atencao',
            'chama mais atenção',
            'mais fragil',
            'mais frágil',
            'mais vulneravel',
            'mais vulnerável',
            'mais critico',
            'mais crítico',
            'ponto mais fraco',
            'ponto academico mais fraco',
            'ponto acadêmico mais fraco',
            'mais claro',
        )
    )
    academic_progression_query = _looks_like_academic_progression_query_local(
        request.message,
        conversation_context=conversation_context,
    )
    focused_student = _resolve_linked_student_candidate(
        actor=actor,
        conversation_context=conversation_context,
        allow_recent_context=False,
        focus=focus,
        focused_student=focused_student,
        mentioned_students=mentioned_students,
    )
    if not (
        _looks_like_family_academic_reason_followup(request.message)
        or _looks_like_family_academic_next_in_line_followup(request.message)
        or family_academic_priority_follow_up
        or family_student_focus_follow_up
        or explicit_single_student_focus
        or cross_student_comparison_follow_up
        or academic_risk_follow_up
        or academic_difficulty_follow_up
        or academic_progression_query
    ):
        return None
    if not (recent_family_academic or recent_family_attendance) and not (
        family_academic_priority_follow_up
        or cross_student_comparison_follow_up
        or academic_risk_follow_up
        or academic_difficulty_follow_up
        or academic_progression_query
    ):
        return None
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return None
    if _wants_upcoming_assessments(request.message) and len(mentioned_students) >= 2:
        selected_names = {_plain_text(name) for name in mentioned_students if str(name).strip()}
        summaries: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        for student in linked_students:
            if not isinstance(student, dict):
                continue
            student_id = str(student.get('student_id') or '').strip()
            full_name = str(student.get('full_name') or '').strip()
            if not student_id or not full_name:
                continue
            normalized_full_name = _plain_text(full_name)
            first_name = normalized_full_name.split(' ')[0] if normalized_full_name else ''
            if normalized_full_name not in selected_names and first_name not in selected_names:
                continue
            academic_payload = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            academic_summary = academic_payload.get('summary') if isinstance(academic_payload, dict) else None
            upcoming_payload = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/upcoming-assessments',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            upcoming_summary = upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else None
            if isinstance(academic_summary, dict) and isinstance(upcoming_summary, dict):
                summaries.append((full_name, academic_summary, upcoming_summary))
        if summaries:
            return _compose_family_upcoming_assessments_focus(summaries)
    if family_student_focus_follow_up or explicit_single_student_focus:
        if isinstance(focused_student, dict):
            student_id = str(focused_student.get('student_id') or '').strip()
            student_name = str(focused_student.get('full_name') or 'Aluno').strip() or 'Aluno'
            if student_id:
                payload = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/academic-summary',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                summary = payload.get('summary') if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    focused_answer = _compose_academic_difficulty_direct_answer(
                        summary,
                        student_name=student_name,
                    ) or _compose_academic_risk_direct_answer(
                        summary,
                        student_name=student_name,
                    )
                    if focused_answer:
                        return focused_answer
    if academic_progression_query and isinstance(focused_student, dict):
        student_id = str(focused_student.get('student_id') or '').strip()
        student_name = str(focused_student.get('full_name') or 'Aluno').strip() or 'Aluno'
        if student_id:
            payload = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            summary = payload.get('summary') if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                progression_answer = _compose_academic_progression_answer_local(
                    summary,
                    student_name=student_name,
                    message=request.message,
                    conversation_context=conversation_context,
                )
                if progression_answer:
                    return progression_answer
    selected_names = {_plain_text(name) for name in mentioned_students if str(name).strip()}
    candidate_students = list(linked_students)
    if selected_names and (
        academic_risk_follow_up
        or academic_difficulty_follow_up
        or explicit_single_student_focus
        or family_student_focus_follow_up
    ):
        filtered_students = [
            student
            for student in candidate_students
            if isinstance(student, dict)
            and (
                _plain_text(str(student.get('full_name') or '')) in selected_names
                or _plain_text(str(student.get('full_name') or '')).split(' ')[0] in selected_names
            )
        ]
        if filtered_students:
            candidate_students = filtered_students
    summaries: list[dict[str, Any]] = []
    for student in candidate_students:
        if not isinstance(student, dict):
            continue
        student_id = str(student.get('student_id') or '').strip()
        if not student_id:
            continue
        payload = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/academic-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        summary = payload.get('summary') if isinstance(payload, dict) else None
        if isinstance(summary, dict):
            summaries.append(summary)
    if cross_student_comparison_follow_up and not explicit_single_student_focus:
        preferred_order = mentioned_students
        if len(preferred_order) < 2:
            recent_name = _recent_linked_student_name_from_messages(conversation_context, actor)
            explicit_other = next(
                (name for name in mentioned_students if _plain_text(name) != _plain_text(recent_name)),
                None,
            ) if recent_name else None
            preferred_order = [item for item in (recent_name, explicit_other) if item]
        comparison_answer = _compose_cross_student_academic_comparison_direct(
            summaries,
            preferred_order=preferred_order,
        )
        if comparison_answer:
            return comparison_answer
    if academic_risk_follow_up or academic_difficulty_follow_up:
        prioritized_students = list(linked_students)
        if isinstance(focused_student, dict):
            prioritized_students = [focused_student, *[student for student in linked_students if student is not focused_student]]
        for student in prioritized_students:
            if not isinstance(student, dict):
                continue
            student_id = str(student.get('student_id') or '').strip()
            full_name = str(student.get('full_name') or '').strip()
            if not student_id or not full_name:
                continue
            full_name_plain = _plain_text(full_name)
            first_name_plain = full_name_plain.split(' ')[0] if full_name_plain else ''
            if student is not focused_student and full_name_plain not in normalized and not (first_name_plain and f' {first_name_plain}' in f' {normalized}'):
                continue
            payload = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            summary = payload.get('summary') if isinstance(payload, dict) else None
            if not isinstance(summary, dict):
                return None
            if academic_risk_follow_up:
                return _compose_academic_risk_direct_answer(summary, student_name=full_name)
            if academic_difficulty_follow_up:
                return _compose_academic_difficulty_direct_answer(summary, student_name=full_name)
            break
    if family_academic_priority_follow_up:
        return _compose_family_academic_focus(summaries)
    if _looks_like_family_academic_reason_followup(request.message):
        return _compose_family_academic_alert_reason(summaries)
    if _looks_like_family_academic_next_in_line_followup(request.message):
        return _compose_family_academic_next_in_line(summaries)
    return None


async def _deterministic_protected_attendance_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    _refresh_native_namespace()
    if request.telegram_chat_id is None:
        return None
    if not isinstance(actor, dict):
        return None
    recent_family_attendance = _recent_family_attendance_context(conversation_context)
    if response.classification.access_tier is AccessTier.public and not recent_family_attendance:
        return None

    focused_student = _focus_marked_student_from_question(actor, request.message)
    mentioned_students = _mentioned_linked_student_names_from_question(actor, request.message)
    focused_student = _resolve_linked_student_candidate(
        actor=actor,
        conversation_context=conversation_context,
        allow_recent_context=recent_family_attendance,
        focus=focus,
        focused_student=focused_student,
        mentioned_students=mentioned_students,
    )
    if _looks_like_family_attendance_aggregate_request(request.message) and not isinstance(focused_student, dict):
        linked_students = actor.get('linked_students')
        if not isinstance(linked_students, list):
            return None
        summaries: list[dict[str, Any]] = []
        for student in linked_students:
            if not isinstance(student, dict):
                continue
            student_id = str(student.get('student_id') or '').strip()
            if not student_id:
                continue
            payload = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            summary = payload.get('summary') if isinstance(payload, dict) else None
            if isinstance(summary, dict):
                summaries.append(summary)
        return _compose_family_attendance_focus(summaries)

    if focus.domain != 'academic' and not recent_family_attendance:
        return None
    if (
        focus.topic != 'attendance'
        and not _question_mentions_unasked_attendance_scope(request.message)
        and not recent_family_attendance
    ):
        return None
    student_id = focus.student_id
    student_name = str(focus.student_name or '').strip() or None
    if isinstance(focused_student, dict):
        student_id = str(focused_student.get('student_id') or '').strip() or student_id
        student_name = str(focused_student.get('full_name') or '').strip() or student_name
    if (not student_id or not student_name) and recent_family_attendance:
        recent_student_name = _recent_linked_student_name_for_admin_finance_combo(conversation_context, actor)
        if recent_student_name and isinstance(actor, dict):
            linked_students = actor.get('linked_students')
            if isinstance(linked_students, list):
                for student in linked_students:
                    if not isinstance(student, dict):
                        continue
                    full_name = str(student.get('full_name') or '').strip()
                    if _plain_text(full_name) != _plain_text(recent_student_name):
                        continue
                    student_id = str(student.get('student_id') or '').strip() or student_id
                    student_name = full_name or student_name
                    break
    if not student_id:
        return None

    payload = await _api_core_get(
        settings=settings,
        path=f'/v1/students/{student_id}/academic-summary',
        params={'telegram_chat_id': request.telegram_chat_id},
    )
    academic_summary = payload.get('summary') if isinstance(payload, dict) else None
    if not isinstance(academic_summary, dict):
        return None
    student_name = str(student_name or academic_summary.get('student_name') or 'Aluno').strip() or 'Aluno'
    if _looks_like_attendance_alert_request(request.message):
        priority_focus = _compose_attendance_priority_focus(academic_summary, student_name=student_name)
        if priority_focus:
            return priority_focus
    if _looks_like_attendance_next_step_request(request.message):
        next_step_focus = _compose_attendance_next_step_focus(academic_summary, student_name=student_name)
        if next_step_focus:
            return next_step_focus
    return None


async def _deterministic_protected_finance_direct_answer(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    actor: dict[str, Any] | None,
    settings: Any,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    _refresh_native_namespace()
    if request.telegram_chat_id is None:
        return None
    if response.classification.access_tier is AccessTier.public:
        return None
    if not isinstance(actor, dict):
        return None
    normalized = _plain_text(request.message)
    unmatched_student = _explicit_unmatched_finance_student_reference(actor, request.message)
    if unmatched_student:
        linked_students = actor.get('linked_students')
        linked_names = [
            str(student.get('full_name') or '').strip()
            for student in linked_students
            if isinstance(student, dict) and str(student.get('full_name') or '').strip()
        ] if isinstance(linked_students, list) else []
        linked_preview = ', '.join(linked_names) if linked_names else 'os alunos vinculados desta conta'
        return (
            f'O que ja aparece: eu nao posso confirmar nem expor o financeiro de {unmatched_student} porque esse aluno nao aparece entre os vinculados desta conta. '
            f'No recorte atual, eu consigo consultar apenas: {linked_preview}. '
            f'Proximo passo: se {unmatched_student} deveria aparecer neste recorte, regularize primeiro o vinculo com a secretaria. '
            'Se a cobranca for de um dos alunos vinculados, me diga qual deles e eu consulto o que ja aparece. '
            'Se a ideia for negociar o restante de uma cobranca vinculada, abra o atendimento com o financeiro pelo canal oficial.'
        )
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-8:]
    )
    combo_followup_terms = (
        'regularizar',
        'proximo passo',
        'próximo passo',
        'em aberto',
        'bloqueio',
        'bloqueando atendimento',
        'nada estiver bloqueando',
        'se nada estiver bloqueando',
        'fala isso de forma direta',
    )
    combo_context = (
        (
            any(term in recent_blob for term in ('documentacao', 'documentação', 'documental', 'cadastro'))
            and any(term in recent_blob for term in ('financeiro', 'fatura', 'faturas', 'mensalidade', 'boleto', 'boletos'))
        )
        or 'panorama combinado de documentacao e financeiro' in recent_blob
        or 'panorama combinado de documentação e financeiro' in recent_blob
    )
    combo_followup = combo_context and any(term in normalized for term in combo_followup_terms)
    if combo_followup:
        linked_students = actor.get('linked_students')
        if not isinstance(linked_students, list):
            return None
        target_student: dict[str, Any] | None = None
        recent_student_name = _recent_linked_student_name_for_admin_finance_combo(conversation_context, actor)
        for student in linked_students:
            if not isinstance(student, dict):
                continue
            full_name = str(student.get('full_name') or '').strip()
            if not full_name:
                continue
            if _plain_text(full_name) in normalized:
                target_student = student
                break
        if target_student is None and recent_student_name:
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                full_name = str(student.get('full_name') or '').strip()
                if _plain_text(full_name) == _plain_text(recent_student_name):
                    target_student = student
                    break
        if isinstance(target_student, dict):
            student_id = str(target_student.get('student_id') or '').strip()
            student_name = str(target_student.get('full_name') or 'Aluno').strip() or 'Aluno'
            if student_id:
                admin_payload = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/administrative-status',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                finance_payload = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/financial-summary',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
                finance_summary = finance_payload.get('summary') if isinstance(finance_payload, dict) else None
                if any(term in normalized for term in ('nada estiver bloqueando', 'se nada estiver bloqueando', 'fala isso de forma direta')):
                    block_parts: list[str] = []
                    if isinstance(admin_summary, dict) and str(admin_summary.get('overall_status') or '').strip().lower() in {'pending', 'review', 'missing', 'incomplete'}:
                        block_parts.append(f'Hoje ainda existe bloqueio administrativo ou documental no recorte de {student_name}.')
                    elif isinstance(finance_summary, dict) and int(finance_summary.get('overdue_invoice_count', 0) or 0) > 0:
                        block_parts.append(f'Hoje existe bloqueio financeiro por atraso vencido no recorte de {student_name}.')
                    elif isinstance(admin_summary, dict) or isinstance(finance_summary, dict):
                        block_parts.append(f'Hoje nao ha bloqueio administrativo ou financeiro no recorte de {student_name}.')
                    if block_parts:
                        return ' '.join(block_parts)
                focused = _compose_admin_finance_focus(
                    admin_summary=admin_summary if isinstance(admin_summary, dict) else None,
                    finance_summary=finance_summary if isinstance(finance_summary, dict) else None,
                    student_name=student_name,
                )
                if focused:
                    return focused
    if not _looks_like_family_finance_aggregate_request(request.message):
        return None
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return None
    summaries: list[dict[str, Any]] = []
    for student in linked_students:
        if not isinstance(student, dict):
            continue
        student_id = str(student.get('student_id') or '').strip()
        if not student_id:
            continue
        payload = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/financial-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        summary = payload.get('summary') if isinstance(payload, dict) else None
        if isinstance(summary, dict):
            summaries.append(summary)
    return _compose_family_finance_focus(summaries)


async def _build_supplemental_focus(
    *,
    settings: Any,
    request: MessageResponseRequest,
    focus: AnswerFocusState,
    school_profile: dict[str, Any] | None = None,
    actor: dict[str, Any] | None = None,
    conversation_context: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    _refresh_native_namespace()
    if focus.topic == 'attendance_justification':
        return {
            'focused_draft': (
                'Para justificar faltas, a escola aceita atestado médico ou odontológico formal. '
                'Um atestado de "ficar dormindo" não serve como justificativa válida. '
                'Se houver dúvida, o documento deve ser apresentado à secretaria da escola.'
            ),
            'evidence_lines': ['Política pública | justificativa de faltas exige documento médico formal'],
        }
    if focus.domain == 'public' and focus.topic == 'known_unknown':
        known_unknown_key = detect_public_known_unknown_key(request.message)
        focused_draft = compose_public_known_unknown_answer(
            key=known_unknown_key or '',
            school_name=str((school_profile or {}).get('school_name') or 'Colegio Horizonte'),
        )
        if focused_draft:
            return {
                'focused_draft': focused_draft,
                'evidence_lines': [f'Conhecido indisponível | {known_unknown_key or "nao_informado"}'],
            }
    if focus.domain == 'public' and focus.topic == 'pricing':
        focused_draft = _compose_public_pricing_focus(
            school_profile=school_profile,
            focus=focus,
            request_message=request.message,
        )
        if not focused_draft:
            return None
        return {
            'focused_draft': focused_draft,
            'evidence_lines': [f'Foco resolvido | {focused_draft}'],
        }
    if (
        request.telegram_chat_id is not None
        and (
            focus.asks_family_aggregate
            or _looks_like_family_attendance_aggregate_request(request.message)
            or focus.topic == 'admin_finance_combo'
        )
        and not focus.student_id
        and isinstance(actor, dict)
    ):
        linked_students = actor.get('linked_students')
        if isinstance(linked_students, list):
            if focus.topic == 'upcoming_assessments':
                summaries: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
                for student in linked_students:
                    if not isinstance(student, dict):
                        continue
                    student_id = str(student.get('student_id') or '').strip()
                    student_name = str(student.get('full_name') or 'Aluno').strip() or 'Aluno'
                    if not student_id:
                        continue
                    academic_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/academic-summary',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    academic_summary = academic_payload.get('summary') if isinstance(academic_payload, dict) else None
                    upcoming_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/upcoming-assessments',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    upcoming_summary = upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else None
                    if isinstance(academic_summary, dict) and isinstance(upcoming_summary, dict):
                        summaries.append((student_name, academic_summary, upcoming_summary))
                focused_draft = _compose_family_upcoming_assessments_focus(summaries)
                if focused_draft:
                    return {
                        'focused_draft': focused_draft,
                        'evidence_lines': [f'Foco agregado | {focused_draft}'],
                    }
            if focus.topic == 'admin_finance_combo' or _is_admin_finance_combined_query_local(
                _plain_text(request.message)
            ):
                admin_summaries: list[dict[str, Any]] = []
                finance_summaries: list[dict[str, Any]] = []
                for student in linked_students:
                    if not isinstance(student, dict):
                        continue
                    student_id = str(student.get('student_id') or '').strip()
                    if not student_id:
                        continue
                    admin_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/administrative-status',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None
                    if isinstance(admin_summary, dict):
                        admin_summaries.append(admin_summary)
                    finance_payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/financial-summary',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    finance_summary = finance_payload.get('summary') if isinstance(finance_payload, dict) else None
                    if isinstance(finance_summary, dict):
                        finance_summaries.append(finance_summary)
                if admin_summaries or finance_summaries:
                    primary_admin_summary = next(
                        (
                            summary
                            for summary in admin_summaries
                            if str(summary.get('overall_status') or '').strip().lower()
                            in {'pending', 'review', 'missing', 'incomplete'}
                        ),
                        admin_summaries[0] if admin_summaries else None,
                    )
                    focused_draft = _compose_admin_finance_combined_answer_local(
                        admin_summary=primary_admin_summary,
                        finance_summaries=finance_summaries,
                        requested_admin_attribute=None,
                    )
                    if focused_draft:
                        return {
                            'focused_draft': focused_draft,
                            'evidence_lines': [f'Foco agregado | {focused_draft}'],
                        }
            if focus.domain == 'institution':
                summaries = []
                for student in linked_students:
                    if not isinstance(student, dict):
                        continue
                    student_id = str(student.get('student_id') or '').strip()
                    if not student_id:
                        continue
                    payload = await _api_core_get(
                        settings=settings,
                        path=f'/v1/students/{student_id}/administrative-status',
                        params={'telegram_chat_id': request.telegram_chat_id},
                    )
                    summary = payload.get('summary') if isinstance(payload, dict) else None
                    if isinstance(summary, dict):
                        summaries.append(summary)
                focused_draft = _compose_family_admin_focus(summaries)
                if focused_draft:
                    return {
                        'focused_draft': focused_draft,
                        'evidence_lines': [f'Foco agregado | {focused_draft}'],
                    }
            summaries: list[dict[str, Any]] = []
            path_suffix = 'academic-summary' if focus.domain == 'academic' else 'financial-summary'
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                student_id = str(student.get('student_id') or '').strip()
                if not student_id:
                    continue
                payload = await _api_core_get(
                    settings=settings,
                    path=f'/v1/students/{student_id}/{path_suffix}',
                    params={'telegram_chat_id': request.telegram_chat_id},
                )
                summary = payload.get('summary') if isinstance(payload, dict) else None
                if isinstance(summary, dict):
                    summaries.append(summary)
            if focus.domain == 'academic' and (
                focus.topic == 'attendance' or _looks_like_family_attendance_aggregate_request(request.message)
            ):
                focused_draft = _compose_family_attendance_focus(summaries)
            else:
                focused_draft = (
                    _compose_family_academic_focus(summaries)
                    if focus.domain == 'academic'
                    else _compose_family_finance_focus(summaries)
                )
            if focused_draft:
                return {
                    'focused_draft': focused_draft,
                    'evidence_lines': [f'Foco agregado | {focused_draft}'],
                }
    request_plain = _plain_text(request.message)
    recent_blob = ' '.join(
        _plain_text(item)
        for item in (
            _extract_recent_user_messages(conversation_context)
            + _extract_recent_assistant_messages(conversation_context)
        )[-8:]
    )
    combo_repair_followup = (
        any(term in request_plain for term in ('bloqueio', 'bloqueando atendimento', 'nada estiver bloqueando', 'se nada estiver bloqueando', 'fala isso de forma direta'))
        and (
            (
                any(term in recent_blob for term in ('documentacao', 'documentação', 'documental', 'cadastro'))
                and any(term in recent_blob for term in ('financeiro', 'fatura', 'faturas', 'mensalidade', 'boleto', 'boletos'))
            )
            or 'panorama combinado de documentacao e financeiro' in recent_blob
            or 'panorama combinado de documentação e financeiro' in recent_blob
        )
    )
    effective_student_id = focus.student_id
    effective_student_name = focus.student_name or 'Aluno'
    if not effective_student_id and combo_repair_followup and isinstance(actor, dict):
        linked_students = actor.get('linked_students')
        recent_student_name = _recent_linked_student_name_from_messages(conversation_context, actor)
        if isinstance(linked_students, list) and recent_student_name:
            normalized_recent_name = _plain_text(recent_student_name)
            for student in linked_students:
                if not isinstance(student, dict):
                    continue
                full_name = str(student.get('full_name') or '').strip()
                if not full_name:
                    continue
                normalized_full_name = _plain_text(full_name)
                first_name = normalized_full_name.split(' ')[0] if normalized_full_name else ''
                if normalized_full_name == normalized_recent_name or (first_name and first_name == normalized_recent_name):
                    candidate_student_id = str(student.get('student_id') or '').strip()
                    if candidate_student_id:
                        effective_student_id = candidate_student_id
                        effective_student_name = full_name
                        break
    if request.telegram_chat_id is None or not effective_student_id:
        return None
    base_params = {'telegram_chat_id': request.telegram_chat_id}
    academic_payload = finance_payload = admin_payload = upcoming_payload = None
    needs_academic = focus.domain == 'academic'
    needs_finance = focus.domain == 'finance'
    needs_admin = focus.domain == 'institution' and focus.topic == 'administrative_status'
    needs_combo = (focus.domain == 'institution' and focus.topic == 'admin_finance_combo') or combo_repair_followup
    if focus.topic == 'attendance_justification':
        needs_admin = False
    tasks: list[asyncio.Future] = []
    task_names: list[str] = []
    if needs_academic or focus.topic in {'attendance_justification'}:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{effective_student_id}/academic-summary', params=base_params))
        task_names.append('academic')
    if needs_finance or needs_combo:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{effective_student_id}/financial-summary', params=base_params))
        task_names.append('finance')
    if needs_admin or needs_combo:
        tasks.append(_api_core_get(settings=settings, path=f'/v1/students/{effective_student_id}/administrative-status', params=base_params))
        task_names.append('admin')
    results = await asyncio.gather(*tasks) if tasks else []
    for name, payload in zip(task_names, results, strict=False):
        if name == 'academic':
            academic_payload = payload
        elif name == 'finance':
            finance_payload = payload
        elif name == 'admin':
            admin_payload = payload

    academic_summary = academic_payload.get('summary') if isinstance(academic_payload, dict) else None
    finance_summary = finance_payload.get('summary') if isinstance(finance_payload, dict) else None
    admin_summary = admin_payload.get('summary') if isinstance(admin_payload, dict) else None

    if focus.topic == 'upcoming_assessments':
        subject_code = _subject_code_from_payload(academic_summary, focus.subject_name)
        upcoming_payload = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{effective_student_id}/upcoming-assessments',
            params={**base_params, **({'subject_code': subject_code} if subject_code else {})},
        )

    focused_draft: str | None = None
    evidence_lines: list[str] = []
    if isinstance(academic_summary, dict) and focus.unknown_subject_name:
        grades = academic_summary.get('grades')
        available_subjects = [
            str(row.get('subject_name') or '').strip()
            for row in grades or []
            if isinstance(row, dict) and str(row.get('subject_name') or '').strip()
        ]
        available_subjects = list(dict.fromkeys(available_subjects))
        preview = ', '.join(available_subjects[:6])
        focused_draft = (
            f'Não encontrei a disciplina {focus.unknown_subject_name} para {focus.student_name or "o aluno"} neste registro.'
            + (f' As disciplinas disponíveis aqui incluem: {preview}.' if preview else '')
        )
    elif isinstance(academic_summary, dict) and focus.topic == 'grades':
        if _question_mentions_timeframe_scope(request.message):
            focused_draft = _compose_grade_timeframe_focus(
                academic_summary,
                student_name=effective_student_name,
                subject_name=focus.subject_name,
            )
        if not focused_draft:
            focused_draft = (
                _compose_subject_grade_focus(academic_summary, student_name=effective_student_name, subject_name=focus.subject_name)
                if focus.subject_name
                else _compose_all_grades_focus(academic_summary, student_name=effective_student_name)
            )
    elif isinstance(academic_summary, dict) and focus.topic == 'attendance':
        focused_draft = _compose_attendance_focus(academic_summary, student_name=effective_student_name)
    elif isinstance(upcoming_payload, dict) and focus.topic == 'upcoming_assessments':
        focused_draft = _compose_upcoming_focus(
            upcoming_payload.get('summary') if isinstance(upcoming_payload, dict) else {},
            student_name=effective_student_name,
            subject_name=focus.subject_name,
            count_only='quant' in _plain_text(request.message),
        )
    elif isinstance(finance_summary, dict) and focus.domain == 'finance':
        focused_draft = _compose_finance_focus(
            finance_summary,
            student_name=effective_student_name,
            next_only=(
                focus.finance_attribute == 'next_due'
                or any(term in _plain_text(request.message) for term in ('proxima', 'próxima', 'proximo', 'próximo'))
            ),
            status_filter=focus.finance_status_filter,
        )
    elif isinstance(admin_summary, dict) and focus.domain == 'institution' and focus.topic == 'administrative_status':
        focused_draft = _compose_administrative_status_focus(
            admin_summary,
            student_name=effective_student_name,
        )
    elif (focus.domain == 'institution' or combo_repair_followup) and isinstance(admin_summary, dict) and isinstance(finance_summary, dict):
        if any(term in request_plain for term in ('nada estiver bloqueando', 'se nada estiver bloqueando', 'fala isso de forma direta')):
            if str(admin_summary.get('overall_status') or '').strip().lower() in {'pending', 'review', 'missing', 'incomplete'}:
                focused_draft = f'Hoje ainda existe bloqueio administrativo ou documental no recorte de {effective_student_name}.'
            elif int(finance_summary.get('overdue_invoice_count', 0) or 0) > 0:
                focused_draft = f'Hoje existe bloqueio financeiro por atraso vencido no recorte de {effective_student_name}.'
            else:
                focused_draft = f'Hoje nao ha bloqueio administrativo ou financeiro no recorte de {effective_student_name}.'
        if not focused_draft:
            focused_draft = _compose_admin_finance_focus(
                admin_summary=admin_summary,
                finance_summary=finance_summary,
                student_name=effective_student_name,
            )

    if focused_draft:
        evidence_lines.append(f'Foco resolvido | {focused_draft}')
    if isinstance(finance_summary, dict):
        open_count = str(finance_summary.get('open_invoice_count') or '')
        overdue_count = str(finance_summary.get('overdue_invoice_count') or '')
        evidence_lines.append(f'Financeiro | aberto={open_count} | vencido={overdue_count}')
    if isinstance(admin_summary, dict):
        evidence_lines.append(
            f"Administrativo | status={str(admin_summary.get('overall_status') or '').strip()} | proximo_passo={str(admin_summary.get('next_step') or '').strip()}"
        )
    if isinstance(upcoming_payload, dict):
        summary = upcoming_payload.get('summary')
        assessments = summary.get('assessments') if isinstance(summary, dict) else None
        if isinstance(assessments, list):
            evidence_lines.append(f'Avaliacoes futuras | total={len(assessments)}')
    return {
        'focused_draft': focused_draft,
        'evidence_lines': [line for line in evidence_lines if line],
    }


def _preserve_deterministic_answer_surface(
    *,
    request: MessageResponseRequest,
    response: MessageResponse,
    focus: AnswerFocusState,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    _refresh_native_namespace()
    candidate_reason = _normalize_text(getattr(response, 'candidate_reason', None))
    response_reason = _normalize_text(getattr(response, 'reason', None))
    reasons = [candidate_reason, response_reason]
    if _is_boundary_answer_surface(*reasons):
        return 'preserve_scope_boundary_surface'
    if _is_restricted_document_surface(*reasons):
        return 'preserve_restricted_document_surface'
    if any(
        (
            'public_bundle.process_compare' in reason
            and ('canonical_lane' in reason or 'process_compare' in reason)
        )
        for reason in reasons
        if reason
    ):
        if _response_covers_requested_scope(request.message, response.message_text):
            return 'preserve_process_compare'
    if any(
        (
            'public_bundle.policy_compare' in reason
            and ('canonical_lane' in reason or 'policy_compare' in reason)
        )
        for reason in reasons
        if reason
    ):
        if _response_covers_requested_scope(request.message, response.message_text):
            return 'preserve_policy_compare'
    if any(
        (
            'public_bundle.integral_study_support' in reason
            and ('canonical_lane' in reason or 'integral_study_support' in reason)
        )
        for reason in reasons
        if reason
    ):
        return 'preserve_integral_study_support'
    if any(
        (
            any(lane in reason for lane in {
                'public_bundle.health_second_call',
                'public_bundle.conduct_frequency_recovery',
                'public_bundle.facilities_study_support',
                'public_bundle.governance_protocol',
                'public_bundle.academic_policy_overview',
                'public_bundle.policy_compare',
                'public_bundle.timeline_lifecycle',
                'public_bundle.year_three_phases',
                'public_bundle.family_new_calendar_assessment_enrollment',
                'public_bundle.first_month_risks',
                'public_bundle.health_authorizations_bridge',
                'public_bundle.secretaria_portal_credentials',
                'public_bundle.bolsas_and_processes',
                'public_bundle.transversal_year',
                'public_bundle.inclusion_accessibility',
                'public_bundle.transport_uniform_bundle',
                'public_bundle.health_emergency_bundle',
                'public_bundle.outings_authorizations',
                'public_bundle.visibility_boundary',
                'public_bundle.access_scope_compare',
                'public_bundle.permanence_family_support',
                'public_bundle.teacher_directory_boundary',
                'public_bundle.calendar_week',
            })
            and 'canonical_lane' in reason
        )
        for reason in reasons
        if reason
    ):
        if _response_covers_requested_scope(request.message, response.message_text):
            return 'preserve_public_canonical_lane'
    if (
        response.mode != OrchestrationMode.clarify
        and _looks_like_explicit_public_pricing_projection(request.message)
        and any(term in _plain_text(response.message_text) for term in ('mensalidade', 'matricula', 'matrícula', 'r$'))
    ):
        return 'preserve_pricing_projection'
    if (
        (
            _looks_like_access_scope_request(request.message)
            or any('access_scope' in _normalize_text(reason) for reason in reasons if reason)
            or 'escopo atual' in _plain_text(response.message_text)
            or 'voce ja esta autenticado' in _plain_text(response.message_text)
        )
        and not _looks_like_student_resolution_failure(response.message_text)
    ):
        return 'preserve_access_scope'
    if any(
        term in _normalize_text(reason)
        for reason in reasons
        if reason
        for term in ('restricted_doc', 'restricted_document')
    ):
        return 'preserve_restricted_document_surface'
    finance_tools = {'get_financial_summary', 'get_student_financial_summary'}
    response_is_finance_surface = (
        response.classification.domain is QueryDomain.finance
        or bool(finance_tools & set(response.selected_tools or []))
        or 'finance' in _normalize_text(getattr(response, 'reason', None))
    )
    if (
        response.classification.access_tier is not AccessTier.public
        and response.mode is OrchestrationMode.structured_tool
        and response_is_finance_surface
        and not _looks_like_student_resolution_failure(response.message_text)
        and not _looks_like_access_scope_request(request.message)
        and focus.topic != 'admin_finance_combo'
        and not focus.finance_status_filter
        and 'valores publicos de referencia' not in _plain_text(response.message_text)
        and _response_covers_requested_scope(request.message, response.message_text)
    ):
        return 'preserve_protected_finance_surface'
    if (
        response.mode != OrchestrationMode.clarify
        and _looks_like_service_routing_bundle_request(request.message)
        and _service_routing_sector_hits(response.message_text) >= 2
        and any(term in _plain_text(response.message_text) for term in ('email', 'telefone', 'whatsapp', 'canal institucional', 'portal autenticado'))
    ):
        return 'preserve_service_routing'
    if (
        request.telegram_chat_id is not None
        and (focus.asks_family_aggregate or _looks_like_family_attendance_aggregate_request(request.message))
        and not focus.student_id
        and response.mode != OrchestrationMode.clarify
        and _response_covers_requested_scope(request.message, response.message_text)
    ):
        response_plain = _plain_text(response.message_text)
        if _looks_like_family_finance_aggregate_request(request.message) and not any(
            term in response_plain
            for term in ('resumo financeiro', 'financeiro', 'fatura', 'boleto', 'mensalidade', 'vencimento')
        ):
            return None
        if _looks_like_family_attendance_aggregate_request(request.message) and not any(
            term in response_plain
            for term in ('frequ', 'falta', 'presen', 'atraso')
        ):
            return None
        linked_students = actor.get('linked_students') if isinstance(actor, dict) else None
        linked_names = [
            _plain_text(str(student.get('full_name') or ''))
            for student in linked_students
            if isinstance(student, dict)
        ] if isinstance(linked_students, list) else []
        mentioned_names = [
            name for name in linked_names
            if name and name.split(' ')[0] in response_plain
        ]
        if (
            len(mentioned_names) >= 2
            or 'contas vinculadas' in response_plain
            or 'alunos vinculados' in response_plain
            or 'meus filhos' in response_plain
        ):
            return 'preserve_family_aggregate'
    return None
