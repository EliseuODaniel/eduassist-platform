from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Protected-domain formatting and answer composition helpers extracted from runtime_core.py."""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import _recent_message_lines, _recent_slot_value
from .intent_analysis_runtime import (
    _contains_any,
    _is_follow_up_query,
    _is_public_curriculum_context_follow_up,
    _is_public_pricing_context_follow_up,
    _message_matches_term,
    _normalize_text,
    _requested_public_features,
    _is_public_curriculum_query,
    _is_public_document_submission_query,
    _is_service_routing_query,
    _wants_academic_grade_requirement,
)
from .reply_experience_runtime import _wants_visual_response
from .public_known_unknowns import detect_public_known_unknown_key
from .protected_summary_runtime import (
    _administrative_checklist_lines,
    _attendance_priority_rows,
    _filter_invoice_rows,
    _format_attendance_overview,
    _format_grades,
    _humanize_invoice_status,
    _parse_invoice_amount,
)


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _public_act_rules_impl(name: str):
    from . import public_act_rules_runtime as _public_act_rules_runtime

    return getattr(_public_act_rules_runtime, name)


def _is_public_calendar_event_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_calendar_event_query as _impl

    return _impl(message)


def _is_public_capacity_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_capacity_query as _impl

    return _impl(message)


def _is_public_policy_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_policy_query as _impl

    return _impl(message)


def _is_public_timeline_query(message: str) -> bool:
    from .public_profile_runtime import _is_public_timeline_query as _impl

    return _impl(message)


def _matches_public_contact_rule(message: str) -> bool:
    from .public_profile_runtime import _count_public_contact_subjects

    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CONTACT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'canais', 'canal', 'falar'}) and (
        _count_public_contact_subjects(message) >= 1
    ):
        return True
    return False


def _matches_public_highlight_rule(message: str) -> bool:
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


def _matches_public_location_rule(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_LOCATION_TERMS)


def _public_profile_impl(name: str):
    from . import public_profile_runtime as _public_profile_runtime

    return getattr(_public_profile_runtime, name)


def _build_public_profile_context(*args, **kwargs):
    return _public_profile_impl('_build_public_profile_context')(*args, **kwargs)


def _resolve_public_profile_act(*args, **kwargs):
    return _public_profile_impl('_resolve_public_profile_act')(*args, **kwargs)


def _parse_iso_date_value(value: Any) -> date | None:
    return _public_profile_impl('_parse_iso_date_value')(value)


def _available_subjects(summary: dict[str, Any]) -> dict[str, dict[str, str]]:
    available_subjects: dict[str, str] = {}
    available_codes: dict[str, str] = {}

    for key in ('grades', 'attendance'):
        rows = summary.get(key)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            subject_name = row.get('subject_name')
            if not isinstance(subject_name, str):
                continue
            normalized_subject = _normalize_text(subject_name)
            available_subjects[normalized_subject] = subject_name
            subject_code = row.get('subject_code')
            if isinstance(subject_code, str) and subject_code.strip():
                available_codes[normalized_subject] = subject_code.strip()
    return {
        normalized_subject: {
            'subject_name': subject_name,
            'subject_code': available_codes.get(normalized_subject, ''),
        }
        for normalized_subject, subject_name in available_subjects.items()
    }


def _subject_filter_from_text(text: str, summary: dict[str, Any]) -> str | None:
    lowered = _normalize_text(text)
    available_subjects = _available_subjects(summary)

    for normalized_subject in available_subjects:
        if normalized_subject in lowered and not re.search(
            rf'\b(?:nao e|nao eh)\s+{re.escape(normalized_subject)}\b',
            lowered,
        ):
            return normalized_subject
        for hint in SUBJECT_HINTS.get(normalized_subject, set()):
            normalized_hint = _normalize_text(hint)
            if normalized_hint in lowered and not re.search(
                rf'\b(?:nao e|nao eh)\s+{re.escape(normalized_hint)}\b',
                lowered,
            ):
                return normalized_subject

    return None


def _detect_academic_focus_kind(message: str) -> str | None:
    if _contains_any(message, UPCOMING_ASSESSMENT_TERMS):
        return 'upcoming'
    if _contains_any(message, ATTENDANCE_TIMELINE_TERMS):
        return 'attendance_timeline'
    if _wants_academic_grade_requirement(message):
        return 'grades'
    normalized = _normalize_text(message)
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
            'fragilizada academicamente',
            'fragilizado academicamente',
            'mais fragilizada academicamente',
            'mais fragilizado academicamente',
            'mais exposta academicamente',
            'mais exposto academicamente',
            'maior risco',
            'pontos de maior risco',
            'mais perto do limite',
            'mais perto da media',
            'mais perto da média',
            'mais proximo do limite',
            'mais próximo do limite',
            'menores medias',
            'menores médias',
            'menor media',
            'menor média',
            'piores medias',
            'piores médias',
            'mais baixas',
            'componentes merecem mais atencao',
            'componentes merecem mais atenção',
            'componentes merecem acompanhamento',
            'componentes exigem mais atencao',
            'componentes exigem mais atenção',
        }
    ):
        return 'grades'
    if _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS):
        return 'attendance'
    if _contains_any(message, GRADE_TERMS):
        return 'grades'
    return None


def _wants_full_grade_overview(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'boletim',
            'quadro inteiro',
            'panorama academico',
            'panorama acadêmico',
            'resumo academico',
            'resumo acadêmico',
            'todas as notas',
            'todas as medias',
            'todas as médias',
        }
    ):
        return True
    asks_grade_list = any(
        _message_matches_term(normalized, term) for term in {'notas', 'medias', 'médias'}
    )
    asks_scope = any(
        _message_matches_term(normalized, term) for term in {'dele', 'dela', 'do aluno', 'da aluna'}
    )
    asks_listing = any(
        _message_matches_term(normalized, term)
        for term in {'mande', 'mostre', 'traga', 'liste', 'lista', 'quais sao', 'quais são'}
    )
    return asks_grade_list and asks_scope and asks_listing


def _extract_unknown_subject_reference(
    message: str,
    *,
    summary: dict[str, Any] | None = None,
) -> str | None:
    normalized = _normalize_text(message)
    if not normalized:
        return None
    normalized_stripped = normalized.strip(' ?.!')
    if _requested_subject_label_from_message(message) is not None:
        return None
    if not any(
        term in normalized for term in UNKNOWN_SUBJECT_CONTEXT_TERMS
    ) and not _is_follow_up_query(message):
        return None
    available_subjects = _available_subjects(summary or {}) if isinstance(summary, dict) else {}
    stopwords = {
        *UNKNOWN_SUBJECT_STOPWORDS,
        *(_normalize_text(alias) for alias in SUBJECT_REQUEST_LABELS),
    }
    patterns = [
        r'^(?:e|mas e|mas|entao|então)\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\s*$',
        r'\baulas?\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
        r'\b(?:notas?|medias?|médias?|provas?|avaliacoes?|avaliações|entregas?)\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
        r'\bem\s+([a-z]{3,}(?:\s+[a-z]{3,})?)\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized_stripped)
        if not match:
            continue
        candidate = _normalize_text(match.group(1))
        if not candidate or candidate in stopwords or candidate in available_subjects:
            continue
        return candidate.title()
    return None


def _recent_missing_academic_subject_context(
    conversation_context: dict[str, Any] | None,
) -> dict[str, str] | None:
    patterns = (
        (
            r'hoje eu nao encontrei notas de (?P<student>.+?) em (?P<subject>.+?) no recorte academico',
            'grades',
        ),
        (
            r'hoje eu nao encontrei registros de frequencia de (?P<student>.+?) em (?P<subject>.+?) no recorte academico',
            'attendance',
        ),
        (
            r'hoje eu nao encontrei proximas avaliacoes de (?P<student>.+?) em (?P<subject>.+?) no recorte academico',
            'upcoming',
        ),
        (
            r'no recorte academico atual, nao encontrei disciplina ou registros de (?P<student>.+?) em (?P<subject>.+?)\.*$',
            'grades',
        ),
    )
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        for pattern, domain_kind in patterns:
            match = re.search(pattern, normalized)
            if not match:
                continue
            student_name = str(match.group('student') or '').strip().title()
            subject_label = str(match.group('subject') or '').strip().title()
            if student_name and subject_label:
                return {
                    'student_name': student_name,
                    'subject_label': subject_label,
                    'kind': domain_kind,
                }
    return None


def _wants_missing_subject_explanation_follow_up(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if _recent_missing_academic_subject_context(conversation_context) is None:
        return False
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'por que nao tem',
            'por que não tem',
            'por que nao apareceu',
            'por que não apareceu',
            'por que nao consta',
            'por que não consta',
            'por que nao veio',
            'por que não veio',
            'por que isso',
            'mas por que',
        }
    )


def _compose_missing_subject_explanation_answer(
    *,
    student_name: str,
    subject_label: str,
) -> str:
    if _normalize_text(subject_label) in {
        'danca',
        'teatro',
        'futebol',
        'volei',
        'maker',
        'laboratorio',
    }:
        return (
            f'Hoje eu nao vejo {subject_label} como disciplina com notas lancadas para {student_name} neste recorte academico. '
            'Isso normalmente significa que ela nao faz parte das materias curriculares registradas para essa turma ou que aparece apenas como atividade/oficina institucional nesta base. '
            f'Se quiser, eu posso listar as disciplinas disponiveis de {student_name} ou verificar o lado institucional de {subject_label}.'
        )
    return (
        f'Hoje eu nao vejo {subject_label} como disciplina com notas lancadas para {student_name} neste recorte academico. '
        'Isso normalmente significa que essa materia nao faz parte das disciplinas registradas para a turma consultada ou que ainda nao houve lancamento nessa base. '
        'Se quiser, eu posso listar as disciplinas disponiveis neste boletim.'
    )


def _looks_like_academic_difficulty_query(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in ACADEMIC_DIFFICULTY_TERMS):
        return False
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_SCOPE_TERMS):
        if not any(
            _message_matches_term(normalized, term)
            for term in {'dele', 'dela', 'do aluno', 'da aluna', 'lucas', 'ana'}
        ):
            return False
    if any(_message_matches_term(normalized, term) for term in ACADEMIC_DIFFICULTY_ANCHORS):
        return True
    recent_active_task = _recent_slot_value(conversation_context, 'active_task') or ''
    return recent_active_task.startswith('academic:') and any(
        _message_matches_term(normalized, term) for term in {'dele', 'dela', 'do aluno', 'da aluna'}
    )


def _message_has_public_followup_signal(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    recent_active_task = _recent_slot_value(conversation_context, 'active_task') or ''
    if recent_active_task.startswith('academic:') and _is_follow_up_query(message):
        if (
            _requested_subject_label_from_message(message) is not None
            or _extract_unknown_subject_reference(message) is not None
            or _wants_missing_subject_explanation_follow_up(
                message,
                conversation_context=conversation_context,
            )
        ):
            return False
    protected_academic_signal = bool(
        _looks_like_subject_existence_query(message)
        or _contains_any(message, GRADE_TERMS | ATTENDANCE_TERMS | UPCOMING_ASSESSMENT_TERMS)
    )
    if protected_academic_signal:
        return False
    return bool(
        _requested_public_features(message)
        or _is_public_curriculum_query(message)
        or _matches_public_contact_rule(message)
        or _matches_public_location_rule(message)
        or _is_service_routing_query(message)
        or _is_public_document_submission_query(message)
        or _is_public_timeline_query(message)
        or _is_public_calendar_event_query(message)
        or _is_public_policy_query(message)
        or _is_public_capacity_query(message)
        or _matches_public_highlight_rule(message)
        or detect_public_known_unknown_key(message)
        or _is_public_pricing_context_follow_up(message, conversation_context=conversation_context)
        or _is_public_curriculum_context_follow_up(
            message, conversation_context=conversation_context
        )
    )


def _should_inherit_academic_attribute_from_context(
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if not _is_follow_up_query(message):
        return False
    if _message_has_public_followup_signal(message, conversation_context=conversation_context):
        return False
    recent_active_task = _recent_slot_value(conversation_context, 'active_task') or ''
    if not recent_active_task.startswith('academic:'):
        return False
    normalized = _normalize_text(message)
    if _extract_unknown_subject_reference(message) is not None:
        return True
    if _wants_missing_subject_explanation_follow_up(
        message,
        conversation_context=conversation_context,
    ):
        return True
    if any(
        _message_matches_term(normalized, term) for term in FOLLOW_UP_REFERENTS | {'dele', 'dela'}
    ):
        return True
    if re.match(r'^(?:e|mas e|mas|entao|então)\s+(?:de|em)\s+[a-z]{3,}', normalized):
        return True
    return False


def _looks_like_finance_open_amount_query(message: str) -> bool:
    normalized = _normalize_text(message)
    payment_terms = {
        'pagar',
        'pagamento',
        'pagamentos',
        'mensalidade',
        'mensalidades',
        'boleto',
        'boletos',
        'fatura',
        'faturas',
        'financeiro',
        'financas',
        'finanças',
        'devendo',
        'devo',
    }
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'quanto falta pagar',
            'quanto falta pra pagar',
            'quanto falta para pagar',
            'falta pagar',
            'falta pra pagar',
            'falta para pagar',
        }
    ):
        return True
    if _wants_academic_grade_requirement(message):
        return False
    if not any(_message_matches_term(normalized, term) for term in payment_terms):
        return False
    return bool(
        any(_message_matches_term(normalized, term) for term in {'quanto', 'valor', 'saldo'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'falta', 'faltando', 'em aberto', 'pendente'}
        )
    )


def _recent_subject_filter_from_context(
    message: str,
    summary: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None,
    focus_kind: str | None,
) -> str | None:
    if not isinstance(conversation_context, dict):
        return None

    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if content.strip() == message.strip():
            continue
        if focus_kind == 'grades' and not (
            _contains_any(content, GRADE_TERMS) or _wants_academic_grade_requirement(content)
        ):
            continue
        if focus_kind in {'attendance', 'attendance_timeline'} and not (
            _contains_any(content, ATTENDANCE_TERMS)
            or _contains_any(content, ATTENDANCE_TIMELINE_TERMS)
        ):
            continue
        if focus_kind == 'upcoming' and not (
            _contains_any(content, UPCOMING_ASSESSMENT_TERMS) or _contains_any(content, GRADE_TERMS)
        ):
            continue
        subject_filter = _subject_filter_from_text(content, summary)
        if subject_filter:
            return subject_filter
    return None


def _detect_subject_filter(
    message: str,
    summary: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
    focus_kind: str | None = None,
) -> str | None:
    direct_filter = _subject_filter_from_text(message, summary)
    if direct_filter:
        return direct_filter
    if _wants_full_grade_overview(message):
        return None
    if _requested_subject_label_from_message(message) is not None:
        return None
    if _extract_unknown_subject_reference(message, summary=summary) is not None:
        return None
    return _recent_subject_filter_from_context(
        message,
        summary,
        conversation_context=conversation_context,
        focus_kind=focus_kind,
    )


def _requested_subject_label_from_message(message: str) -> str | None:
    normalized = _normalize_text(message)
    for alias, label in sorted(
        SUBJECT_REQUEST_LABELS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        normalized_alias = _normalize_text(alias)
        if re.search(rf'\b(?:nao e|nao eh)\s+{re.escape(normalized_alias)}\b', normalized):
            continue
        if _message_matches_term(normalized, alias):
            return label
    return None


def _looks_like_subject_existence_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'isso existe na base',
            'isso existe',
            'tem isso na base',
            'essa disciplina existe',
            'essa materia existe',
            'essa matéria existe',
            'quero saber se isso existe na base',
        }
    )


def _subject_code_for_filter(summary: dict[str, Any], subject_filter: str | None) -> str | None:
    if not subject_filter:
        return None
    available_subjects = _available_subjects(summary)
    subject = available_subjects.get(subject_filter)
    if not isinstance(subject, dict):
        return None
    subject_code = str(subject.get('subject_code', '')).strip()
    return subject_code or None


def _filter_grade_rows(
    summary: dict[str, Any], *, subject_filter: str | None, term_filter: str | None
) -> list[dict[str, Any]]:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return []

    filtered: list[dict[str, Any]] = []
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = _normalize_text(str(grade.get('subject_name', '')))
        term_code = str(grade.get('term_code', ''))
        if subject_filter and subject_name != subject_filter:
            continue
        if term_filter and not term_code.endswith(term_filter):
            continue
        filtered.append(grade)
    return filtered


def _filter_attendance_rows(
    summary: dict[str, Any], *, subject_filter: str | None
) -> list[dict[str, Any]]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return []

    filtered: list[dict[str, Any]] = []
    for row in attendance:
        if not isinstance(row, dict):
            continue
        subject_name = _normalize_text(str(row.get('subject_name', '')))
        if subject_filter and subject_name != subject_filter:
            continue
        filtered.append(row)
    return filtered


def _format_administrative_status(
    summary: dict[str, Any],
    *,
    profile_update: bool,
    requested_attribute: str | None = None,
) -> list[str]:
    if requested_attribute == 'next_step':
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            return [f'Hoje, o proximo passo do seu cadastro e este: {next_step}']
        return ['Hoje eu nao encontrei um proximo passo pendente no seu cadastro.']
    if requested_attribute == 'status':
        overall_status = ADMIN_STATUS_LABELS.get(
            str(summary.get('overall_status', '')).lower(), 'em analise'
        )
        return [f'Situacao administrativa do seu cadastro hoje: {overall_status}.']
    if requested_attribute == 'email':
        email = str(summary.get('profile_email') or 'nao informado')
        return [
            f'Hoje o email cadastral registrado e {email}.',
            'Se precisar atualizar esse dado, o caminho mais seguro continua sendo a secretaria escolar, com confirmacao do titular.',
        ]
    if requested_attribute == 'phone':
        phone = str(summary.get('profile_phone') or 'nao informado')
        return [
            f'O telefone cadastral atual e {phone}.',
            'Se precisar atualizar esse dado, o caminho mais seguro continua sendo a secretaria escolar, com confirmacao do titular.',
        ]
    if requested_attribute == 'documents':
        overall_status = ADMIN_STATUS_LABELS.get(
            str(summary.get('overall_status', '')).lower(), 'em analise'
        )
        lines = [
            f'Situacao administrativa do seu cadastro hoje: {overall_status}.',
            'Situacao documental do seu cadastro hoje:',
        ]
        lines.extend(_administrative_checklist_lines(summary))
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            lines.append(f'Proximo passo: {next_step}')
        return lines
    if profile_update:
        email = str(summary.get('profile_email') or 'nao informado')
        phone = str(summary.get('profile_phone') or 'nao informado')
        lines = [
            f'Hoje o email cadastral registrado e {email}.',
            f'O telefone cadastral atual e {phone}.',
            'Para alterar email ou telefone, o caminho mais seguro e secretaria escolar, porque essa atualizacao ainda exige confirmacao do titular.',
            'Se quiser, eu tambem posso te dizer qual canal da secretaria faz essa tratativa mais rapido.',
        ]
        return lines

    overall_status = ADMIN_STATUS_LABELS.get(
        str(summary.get('overall_status', '')).lower(), 'em analise'
    )
    lines = [f'Situacao administrativa do seu cadastro hoje: {overall_status}.']
    lines.extend(_administrative_checklist_lines(summary))
    next_step = str(summary.get('next_step') or '').strip()
    if next_step:
        lines.append(f'Proximo passo: {next_step}')
    return lines


def _format_student_administrative_status(
    summary: dict[str, Any],
    *,
    requested_attribute: str | None = None,
) -> list[str]:
    student_name = str(summary.get('student_name') or 'o aluno').strip() or 'o aluno'
    overall_status = ADMIN_STATUS_LABELS.get(
        str(summary.get('overall_status', '')).lower(), 'em analise'
    )
    enrollment_code = str(summary.get('enrollment_code') or '').strip()
    guardian_name = str(summary.get('guardian_name') or '').strip()

    if requested_attribute == 'next_step':
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            return [
                f'Hoje {student_name} ainda tem pendencias na documentacao.',
                f'Proximo passo: {next_step}',
            ]
        return [
            f'Hoje eu nao encontrei um proximo passo pendente na documentacao de {student_name}.'
        ]
    if requested_attribute == 'status':
        return [f'Situacao documental de {student_name} hoje: {overall_status}.']
    if requested_attribute == 'documents':
        lines = [f'Situacao documental de {student_name} hoje: {overall_status}.']
        lines.extend(_administrative_checklist_lines(summary))
        next_step = str(summary.get('next_step') or '').strip()
        if next_step:
            lines.append(f'Proximo passo: {next_step}')
        return lines

    lines = [f'Situacao documental de {student_name} hoje: {overall_status}.']
    if enrollment_code:
        lines.append(f'- Matricula: {enrollment_code}')
    if guardian_name:
        lines.append(f'- Responsavel vinculado: {guardian_name}')
    lines.extend(_administrative_checklist_lines(summary))
    next_step = str(summary.get('next_step') or '').strip()
    if next_step:
        lines.append(f'Proximo passo: {next_step}')
    return lines


def _compose_family_admin_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    if not summaries:
        return 'Nao encontrei panorama documental consolidado das contas vinculadas neste recorte.'
    lines = ['Panorama documental das contas vinculadas:']
    pending_students: list[str] = []
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        overall_status = ADMIN_STATUS_LABELS.get(
            str(summary.get('overall_status', '')).lower(), 'em analise'
        )
        next_step = str(summary.get('next_step') or '').strip()
        pending_note = ''
        checklist = summary.get('checklist')
        if isinstance(checklist, list):
            for item in checklist:
                if not isinstance(item, dict):
                    continue
                if str(item.get('status') or '').strip().lower() == 'pending':
                    pending_note = str(item.get('notes') or '').strip()
                    break
        line = f'- {student_name}: situacao documental {overall_status}.'
        if pending_note:
            line += f' Ponto pendente: {pending_note}'
        if next_step:
            line += f' Proximo passo: {next_step}'
        lines.append(line)
        if str(summary.get('overall_status') or '').strip().lower() in {
            'pending',
            'review',
            'missing',
            'incomplete',
        }:
            pending_students.append(student_name)
    if pending_students:
        if len(pending_students) == 1:
            lines.append(
                f'Quem ainda tem pendencia documental mais clara neste recorte: {pending_students[0]}.'
            )
        else:
            lines.append(
                'Quem ainda aparece com pendencia documental neste recorte: '
                + ', '.join(pending_students)
                + '.'
            )
    else:
        lines.append(
            'Hoje nao aparece pendencia documental relevante entre os alunos vinculados neste recorte.'
        )
    return '\n'.join(lines)


def _select_relevant_invoice(
    summary: dict[str, Any],
    *,
    status_filter: set[str] | None,
    prefer_open: bool,
) -> dict[str, Any] | None:
    invoices = _filter_invoice_rows(summary, status_filter=status_filter)
    if not invoices:
        invoices = _filter_invoice_rows(summary, status_filter=None)
    if not invoices:
        return None
    if prefer_open:
        for invoice in invoices:
            if not isinstance(invoice, dict):
                continue
            if str(invoice.get('status', '')).lower() in {'open', 'overdue'}:
                return invoice
    for invoice in invoices:
        if isinstance(invoice, dict):
            return invoice
    return None


def _select_next_due_invoice(
    summary: dict[str, Any],
    *,
    status_filter: set[str] | None,
) -> dict[str, Any] | None:
    open_invoices = _filter_invoice_rows(summary, status_filter={'open'})
    overdue_invoices = _filter_invoice_rows(summary, status_filter={'overdue'})
    candidate_pool = open_invoices or overdue_invoices
    if not candidate_pool:
        return None

    def _invoice_sort_key(invoice: dict[str, Any]) -> tuple[bool, date, str]:
        due_date = _parse_iso_date_value(invoice.get('due_date'))
        return (
            due_date is None,
            due_date or date.max,
            str(invoice.get('reference_month', '')),
        )

    for invoice in sorted(
        (invoice for invoice in candidate_pool if isinstance(invoice, dict)),
        key=_invoice_sort_key,
    ):
        return invoice
    return None


def _compose_academic_attribute_answer(
    summary: dict[str, Any],
    *,
    attribute_request: ProtectedAttributeRequest,
    student_name: str,
    message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if attribute_request.attribute == 'enrollment_code':
        enrollment_code = str(summary.get('enrollment_code', '') or '').strip()
        class_name = str(summary.get('class_name', '') or 'turma nao informada').strip()
        if enrollment_code:
            return f'A matricula de {student_name} e {enrollment_code}. Turma atual: {class_name}.'
        return f'Nao encontrei o codigo de matricula de {student_name} neste recorte autorizado.'
    if attribute_request.attribute == 'attendance':
        normalized_message = _normalize_text(message or '')
        priority_rows = _attendance_priority_rows(summary)
        if priority_rows and any(
            term in normalized_message
            for term in {
                'faltas recentes',
                'ausencias recentes',
                'ausencias',
                'ausências recentes',
                'mais sensivel',
                'mais sensível',
                'principal alerta',
                'maior atencao',
                'maior atenção',
                'mais atencao',
                'mais atenção',
                'quem exige mais atencao',
                'quem exige mais atenção',
                'inspira mais atencao',
                'inspira mais atenção',
                'chama mais atencao',
                'chama mais atenção',
                'chamam atencao',
                'chamam atenção',
                'olhando as faltas',
                'bate na frequencia',
                'bate na frequência',
                'por que a frequencia',
                'por que a frequência',
                'frequencia dele preocupa',
                'frequência dele preocupa',
                'preocupa mais',
                'preocupa menos',
            }
        ):
            top_row = priority_rows[0]
            subject_name = str(top_row.get('subject_name') or 'Disciplina').strip() or 'Disciplina'
            absent = int(top_row.get('absent_count', 0) or 0)
            late = int(top_row.get('late_count', 0) or 0)
            present = int(top_row.get('present_count', 0) or 0)
            return (
                f'O principal alerta de frequencia de {student_name} hoje aparece em {subject_name}: '
                f'{absent} falta(s), {late} atraso(s) e {present} presenca(s) neste recorte. '
                'Esse e o foco principal porque concentra a maior combinacao de faltas e atrasos do aluno neste momento. '
                f'Proximo passo: acompanhar {subject_name} nas proximas aulas para verificar se novas faltas ou atrasos continuam pressionando a frequencia.'
            )
        if _message_matches_term(normalized_message, 'frequencia') and not _contains_any(
            normalized_message, {'falta', 'faltas'}
        ):
            lines = [f'Panorama de frequencia de {student_name}:']
            lines.append('Resumo geral:')
            lines.extend(_format_attendance_overview(summary))
            return '\n'.join(lines)
        attendance = summary.get('attendance')
        absent = 0
        late = 0
        if isinstance(attendance, list):
            for row in attendance:
                if not isinstance(row, dict):
                    continue
                absent += int(row.get('absent_count', 0) or 0)
                late += int(row.get('late_count', 0) or 0)
        return (
            f'Na frequencia de {student_name}, eu encontrei {absent} falta(s) '
            f'e {late} atraso(s) neste recorte.'
        )
    if attribute_request.attribute == 'grades':
        subject_filter = _detect_subject_filter(
            message or '',
            summary,
            conversation_context=conversation_context,
            focus_kind='grades',
        )
        requested_subject_label = _requested_subject_label_from_message(message or '')
        unknown_subject_label = (
            None
            if requested_subject_label
            else _extract_unknown_subject_reference(
                message or '',
                summary=summary,
            )
        )
        missing_subject_label = requested_subject_label or unknown_subject_label
        if missing_subject_label and not subject_filter:
            if _looks_like_subject_existence_query(message or ''):
                return (
                    f'No recorte academico atual, nao encontrei disciplina ou registros '
                    f'de {student_name} em {missing_subject_label}.'
                )
            return (
                f'Hoje eu nao encontrei notas de {student_name} em {missing_subject_label} '
                'no recorte academico desta conta.'
            )
        if subject_filter:
            filtered_summary = dict(summary)
            filtered_summary['grades'] = _filter_grade_rows(
                summary,
                subject_filter=subject_filter,
                term_filter=None,
            )
            lines = [
                f'Notas de {student_name}:',
                f'- Disciplina filtrada: {subject_filter.title()}',
            ]
            lines.extend(_format_grades(filtered_summary))
            return '\n'.join(lines)
        lines = [f'Notas de {student_name}:']
        lines.extend(_format_grades(summary))
        return '\n'.join(lines)
    if attribute_request.attribute == 'grade_requirement':
        return _compose_grade_requirement_answer(
            summary,
            student_name=student_name,
            message=message,
            conversation_context=conversation_context,
        )
    return f'Nao encontrei um atributo academico suportado para {student_name} neste recorte.'


def _compose_finance_attribute_answer(
    summary: dict[str, Any],
    *,
    attribute_request: ProtectedAttributeRequest,
    status_filter: set[str] | None,
    wants_second_copy: bool,
) -> str:
    student_name = str(summary.get('student_name', 'Aluno')).strip() or 'Aluno'
    if attribute_request.attribute == 'contract_code':
        contract_code = str(summary.get('contract_code', '') or '').strip()
        if contract_code:
            return f'O codigo do contrato financeiro de {student_name} e {contract_code}.'
        return f'Nao encontrei o codigo de contrato de {student_name} neste recorte.'

    if attribute_request.attribute == 'next_due':
        invoice = _select_next_due_invoice(summary, status_filter=status_filter)
        if not isinstance(invoice, dict):
            fallback_invoices = [
                item for item in (summary.get('invoices') or []) if isinstance(item, dict)
            ]
            if fallback_invoices:
                fallback_invoices.sort(
                    key=lambda item: (
                        str(item.get('status', '')).lower() not in {'open', 'overdue'},
                        str(item.get('due_date', '')),
                    )
                )
                invoice = fallback_invoices[0]
        if not isinstance(invoice, dict):
            return f'Hoje nao encontrei um proximo pagamento pendente de {student_name}.'
        reference_month = str(invoice.get('reference_month', '') or '---').strip()
        due_date = _format_public_date_text(invoice.get('due_date'))
        amount_due = str(invoice.get('amount_due', '0.00')).strip() or '0.00'
        status = str(invoice.get('status', '')).lower()
        status_label = _humanize_invoice_status(status or 'desconhecido')
        if status == 'open':
            return (
                f'O proximo pagamento de {student_name} hoje e a referencia {reference_month}, '
                f'com vencimento em {due_date} e valor {amount_due}. '
                f'Status atual: {status_label}.'
            )
        return (
            f'Hoje a cobranca pendente mais imediata de {student_name} e a referencia {reference_month}, '
            f'com vencimento em {due_date} e valor {amount_due}. '
            f'Status atual: {status_label}.'
        )

    if attribute_request.attribute == 'open_amount':
        invoices = _filter_invoice_rows(summary, status_filter=status_filter or {'open', 'overdue'})
        outstanding_invoices = [
            invoice
            for invoice in invoices
            if str(invoice.get('status', '')).lower() in {'open', 'overdue'}
        ]
        total_outstanding = sum(
            _parse_invoice_amount(invoice.get('amount_due')) for invoice in outstanding_invoices
        )
        if total_outstanding <= 0:
            return f'Hoje nao encontrei valor em aberto para {student_name} neste recorte.'
        return (
            f'Hoje o valor total em aberto de {student_name} neste recorte e R$ {total_outstanding:.2f}, '
            f'distribuido em {len(outstanding_invoices)} fatura(s).'
        )

    if attribute_request.attribute == 'invoice_id':
        invoice = _select_relevant_invoice(
            summary,
            status_filter=status_filter,
            prefer_open=wants_second_copy or status_filter in ({'open', 'overdue'}, {'overdue'}),
        )
        if not isinstance(invoice, dict):
            return (
                f'Hoje nao encontrei uma fatura compativel de {student_name} '
                'para informar o identificador.'
            )
        invoice_id = str(invoice.get('invoice_id', '') or '').strip()
        reference_month = str(invoice.get('reference_month', '') or '---').strip()
        due_date = str(invoice.get('due_date', '') or '---').strip()
        status_label = _humanize_invoice_status(str(invoice.get('status', 'desconhecido')))
        lines = [
            f'O identificador da fatura mais relevante de {student_name} hoje e {invoice_id}.',
            f'- Referencia: {reference_month}',
            f'- Vencimento: {due_date}',
            f'- Status: {status_label}',
        ]
        if wants_second_copy:
            lines.append(
                'Se quiser a segunda via, eu sigo usando esse identificador como referencia da fatura.'
            )
        return '\n'.join(lines)

    return f'Nao encontrei um atributo financeiro suportado para {student_name} neste recorte.'


def _format_assignments(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma alocacao docente encontrada.']
    lines = []
    for assignment in assignments[:6]:
        if not isinstance(assignment, dict):
            continue
        lines.append(
            '- {class_name} - {subject_name} ({academic_year})'.format(
                class_name=assignment.get('class_name', 'Turma'),
                subject_name=assignment.get('subject_name', 'Disciplina'),
                academic_year=assignment.get('academic_year', '---'),
            )
        )
    return lines or ['- Nenhuma alocacao docente encontrada.']


def _format_unique_classes(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma turma encontrada.']
    seen: set[str] = set()
    lines: list[str] = []
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        class_name = str(assignment.get('class_name', 'Turma'))
        if class_name in seen:
            continue
        seen.add(class_name)
        lines.append(f'- {class_name}')
    return lines or ['- Nenhuma turma encontrada.']


def _format_unique_subjects(summary: dict[str, Any]) -> list[str]:
    assignments = summary.get('assignments')
    if not isinstance(assignments, list) or not assignments:
        return ['- Nenhuma disciplina encontrada.']
    seen: set[str] = set()
    lines: list[str] = []
    for assignment in assignments:
        if not isinstance(assignment, dict):
            continue
        subject_name = str(assignment.get('subject_name', 'Disciplina'))
        if subject_name in seen:
            continue
        seen.add(subject_name)
        lines.append(f'- {subject_name}')
    return lines or ['- Nenhuma disciplina encontrada.']


def _segment_filter_for_teacher_message(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(term in normalized for term in {'ensino medio', 'ensino médio', 'medio', 'médio'}):
        return 'medio'
    if 'fundamental' in normalized or any(
        token in normalized for token in {'6o', '7o', '8o', '9o'}
    ):
        return 'fundamental'
    return None


def _assignment_matches_teacher_segment(
    assignment: dict[str, Any], segment_filter: str | None
) -> bool:
    if not segment_filter:
        return True
    class_name = _normalize_text(str(assignment.get('class_name', '') or ''))
    if segment_filter == 'medio':
        return any(
            token in class_name
            for token in {
                'medio',
                'médio',
                '1a serie',
                '2a serie',
                '3a serie',
                '1a série',
                '2a série',
                '3a série',
                '1em',
                '2em',
                '3em',
            }
        )
    return any(
        token in class_name
        for token in {'fundamental', '6o', '7o', '8o', '9o', '6 ano', '7 ano', '8 ano', '9 ano'}
    )


def _teacher_subject_filter(assignments: list[dict[str, Any]], *, message: str) -> str | None:
    normalized = _normalize_text(message)
    for item in assignments:
        subject_name = str(item.get('subject_name', '') or '').strip()
        if not subject_name:
            continue
        subject_normalized = _normalize_text(subject_name)
        if subject_normalized and subject_normalized in normalized:
            return subject_name
    return None


def _render_teacher_schedule_answer(summary: dict[str, Any], *, message: str) -> str:
    teacher_name = str(summary.get('teacher_name', 'Professor')).strip() or 'Professor'
    assignments = summary.get('assignments') if isinstance(summary.get('assignments'), list) else []
    segment_filter = _segment_filter_for_teacher_message(message)
    subject_filter = _teacher_subject_filter(assignments, message=message)
    filtered = [
        item
        for item in assignments
        if isinstance(item, dict)
        and _assignment_matches_teacher_segment(item, segment_filter)
        and (
            not subject_filter or str(item.get('subject_name', '') or '').strip() == subject_filter
        )
    ]
    normalized = _normalize_text(message)
    if ('so do ensino medio' in normalized or 'só do ensino médio' in normalized) and assignments:
        return (
            'Sim, sua grade atual fica concentrada no Ensino Medio.'
            if len(filtered) == len(assignments)
            else 'Nao. Sua grade atual nao e so do Ensino Medio.'
        )
    if ('so do fundamental' in normalized or 'só do fundamental' in normalized) and assignments:
        return (
            'Sim, sua grade atual fica concentrada no Ensino Fundamental II.'
            if len(filtered) == len(assignments)
            else 'Nao. Sua grade atual nao e so do Ensino Fundamental II.'
        )
    if 'disciplin' in normalized and 'turma' not in normalized and 'classe' not in normalized:
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            subject_name = str(item.get('subject_name', 'Disciplina')).strip()
            if subject_name and subject_name not in seen:
                seen.add(subject_name)
                lines.append(f'- {subject_name}')
        return '\n'.join(
            [f'Disciplinas de {teacher_name}:', *(lines or ['- Nenhuma disciplina encontrada.'])]
        )
    if ('turma' in normalized or 'classe' in normalized) and 'disciplin' not in normalized:
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            class_name = str(item.get('class_name', 'Turma')).strip()
            if class_name and class_name not in seen:
                seen.add(class_name)
                lines.append(f'- {class_name}')
        return '\n'.join(
            [f'Turmas de {teacher_name}:', *(lines or ['- Nenhuma turma encontrada.'])]
        )
    if subject_filter and ('turma' in normalized or 'classe' in normalized):
        seen: set[str] = set()
        lines: list[str] = []
        for item in filtered:
            class_name = str(item.get('class_name', 'Turma')).strip()
            if class_name and class_name not in seen:
                seen.add(class_name)
                lines.append(f'- {class_name}')
        return '\n'.join(
            [
                f'Turmas de {teacher_name} em {subject_filter}:',
                *(lines or ['- Nenhuma turma encontrada.']),
            ]
        )
    lines = [
        '- {class_name} - {subject_name} ({academic_year})'.format(
            class_name=item.get('class_name', 'Turma'),
            subject_name=item.get('subject_name', 'Disciplina'),
            academic_year=item.get('academic_year', '---'),
        )
        for item in filtered[:8]
    ]
    return '\n'.join(
        [
            f'Grade docente de {teacher_name}:',
            *(lines or ['- Nenhuma alocacao docente encontrada.']),
        ]
    )


def _compose_teacher_schedule_summary_answer(
    summary: dict[str, Any],
    *,
    profile: dict[str, Any] | None,
    message: str,
) -> str:
    teacher_name = str(summary.get('teacher_name', 'Professor')).strip() or 'Professor'
    assignments = summary.get('assignments') if isinstance(summary.get('assignments'), list) else []
    filtered = [
        item
        for item in assignments
        if isinstance(item, dict)
        and _assignment_matches_teacher_segment(item, _segment_filter_for_teacher_message(message))
    ]
    classes: list[str] = []
    subjects: list[str] = []
    seen_classes: set[str] = set()
    seen_subjects: set[str] = set()
    for item in filtered:
        class_name = str(item.get('class_name', '') or '').strip()
        subject_name = str(item.get('subject_name', '') or '').strip()
        if class_name and class_name not in seen_classes:
            seen_classes.add(class_name)
            classes.append(class_name)
        if subject_name and subject_name not in seen_subjects:
            seen_subjects.add(subject_name)
            subjects.append(subject_name)
    public_events = (
        (profile or {}).get('public_calendar_events') if isinstance(profile, dict) else None
    )
    event_titles: list[str] = []
    if isinstance(public_events, list):
        for item in public_events:
            if not isinstance(item, dict):
                continue
            title = str(item.get('title', '') or '').strip()
            if title and title not in event_titles:
                event_titles.append(title)
    parts = [
        f'Resumo docente de {teacher_name}: {len(classes)} turma(s) e {len(subjects)} disciplina(s) ativas nesta base.'
    ]
    if subjects:
        parts.append('Disciplinas: ' + ', '.join(subjects[:4]) + '.')
    if classes:
        parts.append('Turmas: ' + ', '.join(classes[:4]) + '.')
    if event_titles:
        parts.append(
            'No calendario publico da escola, vale acompanhar marcos como '
            + ', '.join(event_titles[:3])
            + '.'
        )
    parts.append(
        'No uso do calendario publico da escola, priorize datas institucionais abertas a familias e equipe, como reunioes, simulados, conselhos e janelas letivas publicadas.'
    )
    parts.append(
        'Nos canais oficiais da escola, a secretaria continua sendo o contato institucional mais seguro para comunicacao geral; para alinhamentos pedagogicos, o fluxo correto passa por coordenacao e orientacao conforme o assunto.'
    )
    return ' '.join(part for part in parts if part).strip()


def _build_visual_specialists(*, preview: Any, message: str) -> tuple[InternalSpecialistPlan, ...]:
    if not _wants_visual_response(message):
        return ()

    if preview.classification.domain is QueryDomain.institution:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos publicos institucionais e indicadores visuais',
                tool_names=('build_public_kpi_visual',),
            ),
        )

    if preview.classification.domain is QueryDomain.academic:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos academicos sintetizados a partir do resumo do aluno',
                tool_names=('build_academic_visual',),
            ),
        )

    if preview.classification.domain is QueryDomain.finance:
        return (
            InternalSpecialistPlan(
                name='visual',
                purpose='graficos financeiros sintetizados a partir do resumo do aluno',
                tool_names=('build_finance_visual',),
            ),
        )

    return ()


def _compose_structured_deny(actor: dict[str, Any] | None) -> str:
    if actor is None:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )
    return 'Nao consegui autorizar essa consulta neste contexto. Se precisar, use o portal autenticado da escola.'


async def _compose_student_administrative_status_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any],
    message: str,
    conversation_context: dict[str, Any] | None,
    requested_attribute: str | None,
) -> str:
    student, clarification = _select_linked_student(
        actor,
        message,
        capability='linked',
        conversation_context=conversation_context,
    )
    if clarification is not None:
        return clarification
    if student is None:
        return 'Nao consegui identificar o aluno desta consulta administrativa no Telegram.'
    student_id = student.get('student_id')
    if not isinstance(student_id, str):
        return 'Nao consegui identificar o aluno desta consulta administrativa no Telegram.'
    payload, status_code = await _api_core_get(
        settings=settings,
        path=f'/v1/students/{student_id}/administrative-status',
        params={'telegram_chat_id': request.telegram_chat_id},
    )
    if status_code == 403:
        if requested_attribute in {'documents', 'next_step', None}:
            student_name = str(student.get('full_name') or 'o aluno').strip() or 'o aluno'
            return (
                f'Hoje {student_name} ainda aparece com pendencias administrativas. '
                'Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo '
                'seguir pelo portal autenticado ou pela secretaria escolar.'
            )
        return 'Seu perfil nao tem permissao para consultar a documentacao desse aluno.'
    if status_code != 200 or payload is None:
        student_name = str(student.get('full_name') or 'o aluno').strip() or 'o aluno'
        return (
            f'Hoje {student_name} ainda aparece com pendencias administrativas. '
            'Nao consegui abrir o detalhamento completo agora, mas o proximo passo seguro continua sendo '
            'seguir pelo portal autenticado ou pela secretaria escolar.'
        )

    summary = payload.get('summary', {})
    if not isinstance(summary, dict):
        return 'Nao consegui interpretar o retorno administrativo desse aluno.'
    return '\n'.join(
        _format_student_administrative_status(
            summary,
            requested_attribute=requested_attribute,
        )
    )


def _compose_deterministic_answer(
    *,
    request_message: str,
    preview: Any,
    retrieval_hits: list[Any],
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
    query_hints: set[str],
) -> str:
    if preview.mode is OrchestrationMode.deny:
        if looks_like_restricted_document_query(request_message):
            normalized_message = _normalize_text(request_message)
            if any(
                _message_matches_term(normalized_message, term)
                for term in {'viagem internacional', 'viagem'}
            ):
                return (
                    'Nao. Eu continuo sem acesso ao protocolo interno de viagem internacional de alunos por este canal. '
                    'Se quiser, eu posso orientar pelo material publico correspondente sobre saídas pedagogicas e autorizacoes.'
                )
            if any(
                _message_matches_term(normalized_message, term)
                for term in {
                    'escopo parcial',
                    'responsaveis com escopo parcial',
                    'responsáveis com escopo parcial',
                }
            ):
                return (
                    'Nao posso compartilhar o protocolo interno para responsaveis com escopo parcial por este canal, porque esse material segue restrito. '
                    'No que e publico, a base aberta cobre apenas orientacoes gerais; regras operacionais de permissao, restricao e encaminhamento continuam internas.'
                )
            return (
                'Nao posso compartilhar procedimentos, protocolos, manuais ou playbooks internos da escola por este canal, '
                'porque este perfil nao tem acesso a esse material restrito. '
                'Se quiser, eu posso orientar pelo material publico correspondente.'
            )
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )

    if preview.mode is OrchestrationMode.clarify:
        return (
            f'{DEFAULT_PUBLIC_HELP} Se quiser, pergunte por exemplo: '
            '"quais documentos preciso para a matricula?" ou '
            '"quando acontece a reuniao de pais?".'
        )

    if preview.mode is OrchestrationMode.handoff:
        return (
            'Posso seguir com orientacoes publicas por aqui, mas o handoff humano ainda sera '
            'conectado na proxima etapa. Por enquanto, use a secretaria ou o portal institucional.'
        )

    sections: list[str] = []
    timeline_query = (
        preview.classification.domain is QueryDomain.calendar
        and _is_public_timeline_query(request_message)
    )

    if (
        preview.classification.domain is QueryDomain.calendar
        and calendar_events
        and not timeline_query
    ):
        sections.append('Encontrei estes proximos eventos publicos no calendario escolar:')
        sections.extend(_format_event_line(event) for event in calendar_events[:3])

    if retrieval_hits:
        intro = 'Segundo a base institucional atual:'
        if preview.classification.domain is QueryDomain.calendar and sections:
            intro = 'Tambem localizei estas referencias na base documental:'
        sections.append(intro)
        sections.extend(f'- {hit.text_excerpt}' for hit in retrieval_hits[:2])

    if not sections:
        return _compose_public_gap_answer(query_hints)

    source_lines = _render_source_lines(citations)
    if source_lines:
        sections.append(source_lines)
    return '\n'.join(sections)


def _school_name_from_profile(profile: dict[str, Any] | None) -> str:
    return (
        str((profile or {}).get('school_name', 'Colegio Horizonte')).strip() or 'Colegio Horizonte'
    )


def _looks_like_known_unknown_answer(message_text: str) -> bool:
    normalized = _normalize_text(message_text)
    return any(
        marker in normalized
        for marker in (
            'nao esta publicado',
            'nao estao publicados',
            'nao publicam',
            'nao informam',
            'nao divulga',
            'nao divulgam',
        )
    )


def _build_runtime_public_supports(
    *,
    request_message: str,
    school_profile: dict[str, Any] | None,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    public_plan: PublicInstitutionPlan | None,
    selected_tools: list[str],
) -> list[MessageEvidenceSupport]:
    if not isinstance(school_profile, dict) or not school_profile:
        return []
    school_name = _school_name_from_profile(school_profile)
    supports: list[MessageEvidenceSupport] = [
        MessageEvidenceSupport(
            kind='scope',
            label='public_school_profile',
            detail=f'Perfil institucional publico de {school_name}.',
        )
    ]
    primary_act = public_plan.conversation_act if public_plan is not None else None
    secondary_acts = public_plan.secondary_acts if public_plan is not None else ()
    focus_hint = public_plan.focus_hint if public_plan is not None else None
    if not primary_act:
        context = _build_public_profile_context(
            school_profile,
            request_message,
            actor=actor,
            original_message=request_message,
            conversation_context=conversation_context,
            semantic_plan=public_plan,
        )
        primary_act = _resolve_public_profile_act(context)
    if primary_act:
        bundle = build_public_evidence_bundle(
            school_profile,
            primary_act=primary_act,
            secondary_acts=secondary_acts,
            request_message=request_message,
            focus_hint=focus_hint,
        )
        if bundle is not None:
            for fact in bundle.facts[:4]:
                supports.append(
                    MessageEvidenceSupport(
                        kind='profile_fact',
                        label=fact.key,
                        excerpt=fact.text,
                    )
                )
    for tool_name in selected_tools[:2]:
        supports.append(
            MessageEvidenceSupport(
                kind='tool',
                label=tool_name,
                detail='Structured public source checked before composing the answer.',
            )
        )
    return supports[:6]
