from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Student selection and access-scope helpers extracted from reply_experience_runtime.py."""

from . import runtime_core as _runtime_core


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not actor:
        return []
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _student_focus_candidate(actor: dict[str, Any] | None, message: str) -> dict[str, Any] | None:
    matched_students = _matching_students_in_text(_linked_students(actor), message)
    if len(matched_students) != 1:
        return None
    return matched_students[0]


def _student_capability_topics(student: dict[str, Any]) -> list[str]:
    topics: list[str] = []
    if bool(student.get('can_view_academic', False)):
        topics.extend(['notas', 'faltas', 'proximas provas', 'matricula'])
    if bool(student.get('can_view_finance', False)):
        topics.extend(['financeiro', 'boletos'])
    deduped: list[str] = []
    for topic in topics:
        if topic not in deduped:
            deduped.append(topic)
    return deduped


def _is_children_overview_query(message: str, actor: dict[str, Any] | None) -> bool:
    if not _linked_students(actor):
        return False
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'quais meus filhos',
            'quais sao meus filhos',
            'quais são meus filhos',
            'quem sao meus filhos',
            'quem são meus filhos',
            'quem estao vinculados',
            'quem está vinculado',
        }
    ):
        return True
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'meus filhos',
            'meu filho',
            'quais filhos tenho',
            'filhos matriculados',
            'filhos vinculados',
            'alunos vinculados',
        }
    ):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'informacao',
            'informacoes',
            'dados',
            'fornecer',
            'consigo obter',
            'posso obter',
            'matriculados',
            'vinculados',
        }
    )


def _is_student_focus_activation_query(message: str, actor: dict[str, Any] | None) -> bool:
    student = _student_focus_candidate(actor, message)
    if student is None:
        return False
    normalized = _normalize_text(message)
    if any(
        value is not None
        for value in (
            _detect_academic_focus_kind(message),
            _detect_academic_attribute_request(message),
            _detect_finance_attribute_request(message),
        )
    ):
        return False
    if (
        _effective_finance_status_filter(message)
        or _detect_admin_attribute_request(message) is not None
    ):
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'quero falar do',
            'quero falar sobre',
            'falar do',
            'falar sobre',
            'sobre o',
            'sobre a',
            'eu falei',
        }
    ):
        return True
    token_count = len(re.findall(r'[a-z0-9]+', normalized))
    return token_count <= 6


def _should_continue_recent_student_task(
    message: str,
    *,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not _is_student_focus_activation_query(message, actor):
        return False
    recent_focus = _recent_trace_focus(conversation_context)
    if not isinstance(recent_focus, dict):
        return False
    focus_kind = str(recent_focus.get('kind', '') or '').strip()
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    if not _recent_focus_is_fresh(
        conversation_context, focus_kind=focus_kind, active_task=active_task
    ):
        return False
    return active_task.startswith(('academic:', 'finance:', 'admin:'))


def _is_discourse_repair_reset_query(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {
            'cheguei agora',
            'acabei de chegar',
            'acabei de entrar',
            'eu cheguei agora',
            'mas eu cheguei agora',
            'acabei de chegar agora',
        }
    ):
        return False
    recent_focus = _recent_trace_focus(conversation_context)
    if not isinstance(recent_focus, dict):
        return False
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    return active_task.startswith('workflow:')


def _derive_pending_disambiguation(
    *,
    actor: dict[str, Any] | None,
    message: str,
    preview: Any | None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if _is_discourse_repair_reset_query(message, conversation_context):
        return 'workflow_reset'
    if _is_access_scope_query(message) or _is_access_scope_repair_query(
        message, actor, conversation_context
    ):
        return 'access_scope'
    if _is_linked_student_repair_query(message, conversation_context):
        return 'linked_student_repair'
    if _is_children_overview_query(message, actor):
        return 'linked_students_overview'
    linked_students = _linked_students(actor)
    if (
        linked_students
        and not _matching_students_in_text(linked_students, message)
        and _explicit_unmatched_student_reference(
            linked_students,
            message,
            conversation_context=conversation_context,
        )
    ):
        return 'student_reference_unmatched'
    if _is_student_focus_activation_query(
        message, actor
    ) and not _should_continue_recent_student_task(
        message,
        actor=actor,
        conversation_context=conversation_context,
    ):
        return 'student_focus'
    if preview is not None and getattr(preview, 'mode', None) is OrchestrationMode.clarify:
        rescued_domain = _recent_student_disambiguation_domain(conversation_context)
        if rescued_domain is not None:
            return 'student_selection'
    return None


def _compose_linked_students_overview_answer(actor: dict[str, Any] | None) -> str | None:
    students = _linked_students(actor)
    if not students:
        return None
    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    if not names:
        return None
    preview_names = ', '.join(names[:-1]) + f' e {names[-1]}' if len(names) > 1 else names[0]
    capability_topics = _student_capability_topics(students[0])
    capability_text = (
        ', '.join(capability_topics[:6])
        if capability_topics
        else 'informacoes escolares autorizadas'
    )
    return (
        f'Os alunos vinculados a esta conta hoje sao {preview_names}. '
        f'Eu posso consultar {capability_text}, dentro do que sua vinculacao permitir. '
        'Se quiser, me diga direto algo como "notas do Lucas" ou "financeiro da Ana".'
    )


def _compose_authenticated_access_scope_answer(
    actor: dict[str, Any] | None,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str:
    students = _linked_students(actor)
    if not students:
        return (
            'Para consultas protegidas, como notas, faltas, provas e financeiro, voce precisa vincular sua conta do Telegram '
            f'ao portal do {school_name}. No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando '
            '`/start link_<codigo>`. Depois disso, eu passo a consultar seus dados autorizados por este canal.'
        )

    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    preview_names = (
        ', '.join(names[:-1]) + f' e {names[-1]}'
        if len(names) > 1
        else (names[0] if names else 'aluno vinculado')
    )
    topics: list[str] = []
    for student in students:
        for topic in _student_capability_topics(student):
            if topic not in topics:
                topics.append(topic)
    topics_text = ', '.join(topics[:6]) if topics else 'informacoes escolares autorizadas'
    scoped_lines: list[str] = []
    for student in students:
        student_name = str(student.get('full_name', 'Aluno')).strip() or 'Aluno'
        student_scopes: list[str] = []
        if bool(student.get('can_view_academic', False)):
            student_scopes.append('academico')
        if bool(student.get('can_view_finance', False)):
            student_scopes.append('financeiro')
        if student_scopes:
            scoped_lines.append(f'- {student_name}: {", ".join(student_scopes)}')
    return (
        f'Voce ja esta autenticado por aqui e sua conta esta vinculada a {preview_names}. '
        f'Por este canal eu consigo consultar {topics_text}, dentro das permissoes dessa vinculacao. '
        + (' Escopo atual:\n' + '\n'.join(scoped_lines) if scoped_lines else '')
        + ' '
        'Se quiser, me diga algo como "notas do Lucas", "faltas da Ana" ou "financeiro do Lucas".'
    )


def _compose_authenticated_access_scope_followup_answer(actor: dict[str, Any] | None) -> str | None:
    students = _linked_students(actor)
    if not students:
        return None
    scoped_lines: list[str] = []
    for student in students:
        student_name = str(student.get('full_name', 'Aluno')).strip() or 'Aluno'
        student_scopes: list[str] = []
        if bool(student.get('can_view_academic', False)):
            student_scopes.append('academico')
        if bool(student.get('can_view_finance', False)):
            student_scopes.append('financeiro')
        if student_scopes:
            scoped_lines.append(f'- {student_name}: {", ".join(student_scopes)}')
    if not scoped_lines:
        return None
    return 'Por aluno vinculado, hoje o seu escopo fica assim:\n' + '\n'.join(scoped_lines)


def _compose_teacher_access_scope_answer(
    actor: dict[str, Any] | None,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str:
    actor_name = str((actor or {}).get('full_name', 'Professor')).strip() or 'Professor'
    role_code = str((actor or {}).get('role_code', '') or '').strip().lower()
    if role_code == 'teacher':
        return (
            f'Voce esta falando aqui como {actor_name}, no perfil de professor do {school_name}. '
            'No Telegram, nesta etapa eu consigo consultar sua grade docente, turmas e disciplinas. '
            'A situacao individual dos alunos ainda nao esta liberada por este canal. '
            'Se quiser, me pergunte "qual meu horario?", "quais sao minhas turmas?" ou "quais disciplinas eu ministro?".'
        )
    return (
        f'Se voce ja e professor do {school_name}, o acesso docente depende da vinculacao da conta institucional correta no Telegram. '
        'Nesta conta atual eu nao identifiquei um perfil docente ativo. '
        'Quando a vinculacao de professor estiver correta, por aqui eu consigo consultar horario, turmas e disciplinas; '
        'a situacao individual dos alunos continua fora do escopo deste canal nesta etapa.'
    )


def _compose_public_access_scope_answer(
    actor: dict[str, Any] | None,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str:
    return _compose_authenticated_access_scope_answer(actor, school_name=school_name)


def _humanize_actor_role(role_code: str | None) -> str:
    normalized = str(role_code or '').strip().lower()
    return {
        'guardian': 'responsavel',
        'student': 'aluno',
        'teacher': 'professor',
        'finance': 'financeiro',
        'coordinator': 'coordenacao',
        'admin': 'administracao',
    }.get(normalized, normalized or 'usuario autenticado')


def _compose_actor_identity_answer(actor: dict[str, Any] | None) -> str:
    if not actor:
        return (
            'Eu ainda nao consegui confirmar a identidade desta conta no Telegram. '
            'Se quiser, tente novamente em instantes ou refaca a vinculacao pelo portal.'
        )
    actor_name = str(actor.get('full_name', 'Usuario')).strip() or 'Usuario'
    role_label = _humanize_actor_role(actor.get('role_code'))
    students = _linked_students(actor)
    if not students:
        return (
            f'Voce esta falando aqui como {actor_name}, no perfil de {role_label}. '
            'No momento eu nao encontrei alunos vinculados a esta conta para consulta protegida.'
        )
    names = [str(student.get('full_name', 'Aluno')).strip() for student in students]
    names = [name for name in names if name]
    preview_names = ', '.join(names[:-1]) + f' e {names[-1]}' if len(names) > 1 else names[0]
    topics: list[str] = []
    for student in students:
        for topic in _student_capability_topics(student):
            if topic not in topics:
                topics.append(topic)
    topics_text = ', '.join(topics[:6]) if topics else 'informacoes escolares autorizadas'
    return (
        f'Voce esta falando aqui como {actor_name}, no perfil de {role_label}. '
        f'Sua conta esta vinculada a {preview_names}. '
        f'Por aqui eu consigo consultar {topics_text}, dentro das permissoes dessa vinculacao.'
    )


def _compose_account_context_answer(
    actor: dict[str, Any] | None,
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    if _is_children_overview_query(request_message, actor):
        overview = _compose_linked_students_overview_answer(actor)
        if overview:
            return overview
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if str(
        recent_focus.get('active_task', '') or ''
    ).strip() == 'admin:access_scope' and _is_access_scope_query(request_message):
        followup_scope = _compose_authenticated_access_scope_followup_answer(actor)
        if followup_scope:
            return followup_scope
    normalized = _normalize_text(request_message)
    if any(
        _message_matches_term(normalized, term)
        for term in {'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver sobre cada um'}
    ):
        followup_scope = _compose_authenticated_access_scope_followup_answer(actor)
        if followup_scope:
            return followup_scope
    if _is_access_scope_query(request_message) or _is_access_scope_repair_query(
        request_message,
        actor,
        conversation_context,
    ):
        return _compose_authenticated_access_scope_answer(actor)
    return _compose_actor_identity_answer(actor)


def _compose_student_focus_activation_answer(
    actor: dict[str, Any] | None,
    *,
    student_name: str | None,
) -> str | None:
    if not student_name:
        return None
    student = _student_focus_candidate(actor, student_name) or next(
        (
            item
            for item in _linked_students(actor)
            if _normalize_text(str(item.get('full_name', ''))) == _normalize_text(student_name)
        ),
        None,
    )
    topics = _student_capability_topics(student or {})
    if topics:
        topics_text = ', '.join(topics[:6])
        return (
            f'Perfeito, seguimos com {student_name}. '
            f'Posso te ajudar com {topics_text}. '
            'Se quiser, ja me diga o que voce quer ver primeiro.'
        )
    return (
        f'Perfeito, seguimos com {student_name}. '
        'Se quiser, me diga agora qual assunto voce quer ver sobre esse aluno.'
    )


def _compose_workflow_reset_answer() -> str:
    return (
        'Sem problema, vamos comecar do zero entao. '
        'Se voce quiser atendimento humano por aqui, me diga em uma frase curta qual e o assunto '
        'como financeiro, secretaria, matricula ou direcao, e eu sigo desse ponto.'
    )


def _compose_linked_student_repair_answer(actor: dict[str, Any] | None) -> str | None:
    students = _linked_students(actor)
    if not students:
        return None
    options = _format_student_options(students)
    return (
        'Entendi. Pelo que aparece nesta vinculacao do Telegram, eu so encontrei estes alunos liberados para consulta: '
        f'{options}. '
        'Se o aluno que voce esperava nao apareceu aqui, vale revisar a vinculacao no portal ou com a secretaria. '
        'Se quiser, eu posso continuar agora com qualquer um desses alunos.'
    )


def _should_use_student_administrative_status(
    actor: dict[str, Any] | None,
    message: str,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    students = _linked_students(actor)
    if not students:
        return False
    if _matching_students_in_text(students, message):
        return True
    if _explicit_unmatched_student_reference(
        students,
        message,
        conversation_context=conversation_context,
    ):
        return True
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {'meu filho', 'minha filha', 'aluno', 'aluna'}
    ):
        return True
    if not _is_follow_up_query(message):
        return False
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if (
        str(recent_focus.get('active_task', '') or '').strip()
        == 'admin:student_administrative_status'
    ):
        return True
    if _recent_slot_value(conversation_context, 'admin_attribute'):
        return True
    return any(
        _recent_slot_value(conversation_context, key)
        for key in ('academic_student_name', 'finance_student_name')
    )


def _recent_assistant_auth_context(conversation_context: dict[str, Any] | None) -> bool:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'portal do aluno',
                'portal do responsavel',
                'portal do aluno ou responsavel',
                'portal autenticado',
                'vincular sua conta',
                'acessar o portal',
                'acesse o portal',
            }
        ):
            return True
    return False


def _recent_assistant_unmatched_student_context(
    conversation_context: dict[str, Any] | None,
) -> bool:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'assistant':
            continue
        normalized = _normalize_text(content)
        if _message_matches_term(normalized, 'nao encontrei') and _message_matches_term(
            normalized, 'alunos vinculados'
        ):
            return True
    return False


def _is_access_scope_repair_query(
    message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not _linked_students(actor):
        return False
    if not _recent_assistant_auth_context(conversation_context):
        return False
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'ja me autentiquei',
            'já me autentiquei',
            'ja estou autenticado',
            'já estou autenticado',
            'mas e meu filho',
            'mas é meu filho',
            'esta matriculado como meu filho',
            'está matriculado como meu filho',
        }
    )


def _is_teacher_scope_guidance_query(
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    user: UserContext | None = None,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if _looks_like_teacher_internal_scope_query(message):
        return True
    actor_role = str((actor or {}).get('role_code', '') or '').strip().lower()
    user_role = user.role.value if isinstance(user, UserContext) else ''
    teacher_session = actor_role == 'teacher' or (
        isinstance(user, UserContext) and user.authenticated and user_role == UserRole.teacher.value
    )
    if not teacher_session:
        return False
    normalized = _normalize_text(message)
    if _is_access_scope_query(message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'meu horario',
            'meu horário',
            'meus horarios',
            'meus horários',
            'meu horario de aula',
            'meu horário de aula',
            'meus horarios de aula',
            'meus horários de aula',
            'minhas turmas',
            'minhas disciplinas',
            'grade docente',
            'grade completa',
            'minha grade',
            'minha grade docente',
            'meus alunos',
            'quais turmas',
            'quais disciplinas',
            'quais classes',
            'classes',
            'alocacao',
            'alocação',
            'rotina',
            'rotina docente',
        }
    ):
        return True
    if not _recent_teacher_scope_context(conversation_context):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'e so do ensino medio',
            'e só do ensino médio',
            'so do ensino medio',
            'só do ensino médio',
            'e so do medio',
            'e só do médio',
            'so do medio',
            'só do médio',
            'e so do fundamental',
            'e só do fundamental',
            'so do fundamental',
            'só do fundamental',
            'e as turmas',
            'e as disciplinas',
            'e quais turmas',
            'e quais disciplinas',
            'e quais classes',
        }
    )


def _should_fetch_teacher_schedule(
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    user: UserContext | None = None,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if not _is_teacher_scope_guidance_query(
        message,
        actor=actor,
        user=user,
        conversation_context=conversation_context,
    ):
        return False
    if _is_access_scope_query(message):
        return False
    normalized = _normalize_text(message)
    if _contains_any(message, TEACHER_SCHEDULE_TERMS):
        return True
    if _recent_teacher_scope_context(conversation_context):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'medio',
            'médio',
            'fundamental',
            'rotina docente',
            'minha rotina docente',
            'minha grade docente',
            'grade docente completa',
            'quais turmas eu atendo',
            'quais disciplinas eu atendo',
            'quais classes eu atendo',
            'quais turmas e disciplinas eu tenho',
            'quais turmas e disciplinas eu atendo',
        }
    )


def _is_linked_student_repair_query(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if not _recent_assistant_unmatched_student_context(conversation_context):
        return False
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'mas e meu filho',
            'mas é meu filho',
            'esta matriculado como meu filho',
            'está matriculado como meu filho',
            'mas ele e meu filho',
            'mas ele é meu filho',
        }
    )


def _compose_contextual_clarify_answer(
    *,
    request_message: str,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    slot_memory: ConversationSlotMemory,
) -> str | None:
    if (
        actor is not None
        and _linked_students(actor)
        and (
            _is_access_scope_query(request_message)
            or _is_access_scope_repair_query(request_message, actor, conversation_context)
        )
    ):
        return _compose_authenticated_access_scope_answer(actor)
    if slot_memory.pending_disambiguation == 'workflow_reset':
        return _compose_workflow_reset_answer()
    if slot_memory.pending_disambiguation == 'access_scope':
        return _compose_public_access_scope_answer(actor)
    if slot_memory.pending_disambiguation == 'linked_student_repair':
        return _compose_linked_student_repair_answer(actor)
    if slot_memory.pending_disambiguation == 'linked_students_overview':
        return _compose_linked_students_overview_answer(actor)
    if slot_memory.pending_disambiguation == 'student_reference_unmatched':
        students = _linked_students(actor)
        requested_name = _explicit_unmatched_student_reference(
            students,
            request_message,
            conversation_context=conversation_context,
        )
        if students and requested_name:
            return _compose_unmatched_student_reference_answer(
                requested_name=requested_name,
                students=students,
            )
    if slot_memory.pending_disambiguation == 'student_focus':
        if _should_continue_recent_student_task(
            request_message,
            actor=actor,
            conversation_context=conversation_context,
        ):
            return None
        student_name = slot_memory.academic_student_name or slot_memory.finance_student_name
        return _compose_student_focus_activation_answer(actor, student_name=student_name)
    if slot_memory.pending_disambiguation == 'student_selection':
        rescued_domain = _recent_student_disambiguation_domain(conversation_context)
        if rescued_domain is QueryDomain.finance:
            return 'Perfeito. Me diga qual aluno voce quer consultar no financeiro e eu sigo por esse caminho.'
        if rescued_domain is QueryDomain.academic:
            return 'Perfeito. Me diga qual aluno voce quer consultar e eu sigo por notas, faltas ou provas dele.'
    return None


def _eligible_students(actor: dict[str, Any] | None, *, capability: str) -> list[dict[str, Any]]:
    students = _linked_students(actor)
    if capability == 'academic':
        return [student for student in students if bool(student.get('can_view_academic', False))]
    if capability == 'finance':
        return [student for student in students if bool(student.get('can_view_finance', False))]
    return students


def _student_matches_text(student: dict[str, Any], text: str) -> bool:
    normalized_text = _normalize_text(text)
    full_name = str(student.get('full_name', ''))
    enrollment_code = str(student.get('enrollment_code', ''))
    normalized_name = _normalize_text(full_name)
    if normalized_name and normalized_name in normalized_text:
        return True
    if enrollment_code and enrollment_code.lower() in normalized_text:
        return True
    return False


def _student_name_tokens(student: dict[str, Any]) -> list[str]:
    full_name = _normalize_text(str(student.get('full_name', '')))
    return [token for token in re.findall(r'[a-z0-9]+', full_name) if len(token) >= 3]


def _is_student_reference_context_message(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'meu filho',
            'minha filha',
            'aluno',
            'aluna',
            'nota',
            'notas',
            'falta',
            'faltas',
            'prova',
            'provas',
            'boletim',
            'frequencia',
            'frequência',
            'matricula',
            'matrícula',
            'financeiro',
            'boleto',
            'boletos',
            'fatura',
            'faturas',
            'mensalidade',
            'pagamento',
            'vencimento',
            'contrato',
        }
    )


def _extract_explicit_student_reference_candidates(message: str) -> list[str]:
    normalized = _normalize_text(message)
    patterns = [
        (r'e\s+se\s+eu\s+perguntar\s+do\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', True),
        (r'(?:sobre o|sobre a|do|da)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', True),
        (r'(?:meu filho|minha filha|aluno|aluna)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})', False),
        (
            r'(?:e o|e a)\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2}?)(?=\s+(?:como|qual|quais|quanto|quantas|quantos|que|serve|esta|está|tem|fica|ficou)\b|[?!.,;:]|$)',
            True,
        ),
    ]
    candidates: list[str] = []
    stopwords = {
        'a',
        'agora',
        'ai',
        'aí',
        'autenticado',
        'autenticada',
        'autentiquei',
        'com',
        'da',
        'de',
        'do',
        'e',
        'eu',
        'falei',
        'falar',
        'ja',
        'já',
        'mas',
        'me',
        'meu',
        'meus',
        'minha',
        'minhas',
        'filho',
        'filha',
        'notas',
        'academico',
        'acadêmico',
        'escopo',
        'faltas',
        'financeiro',
        'boletos',
        'dados',
        'informacoes',
        'informações',
        'matricula',
        'matrícula',
        'documentacao',
        'documentação',
        'documentos',
        'atendimento',
        'bloqueando',
        'bloqueio',
        'regular',
        'regularidade',
        'pagamento',
        'pagamentos',
        'familia',
        'família',
        'responsavel',
        'responsável',
        'professor',
        'professora',
        'docente',
        'manual',
        'interno',
        'material',
        'comunicacao',
        'comunicação',
        'pedagogica',
        'pedagógica',
        'registro',
        'registros',
        'avaliacao',
        'avaliação',
        'avaliacoes',
        'avaliações',
        'dele',
        'dela',
        'hoje',
        'atual',
        'atualmente',
        'data',
        'datas',
        'proximo',
        'proxima',
        'próximo',
        'próxima',
        'vencimento',
        'vencimentos',
        'boleto',
        'contrato',
        'telefone',
        'email',
        'horario',
        'horário',
        'quero',
        'saber',
        'se',
        'so',
        'só',
        'como',
        'qual',
        'quais',
        'quanto',
        'quantas',
        'quantos',
        'que',
        'serve',
        'esta',
        'está',
        'sensivel',
        'sensível',
        'recente',
        'recentes',
        'mais',
        'perguntar',
        'pergunto',
        'sobre',
        'ta',
        'tá',
        'ver',
        'vinculado',
        'vinculada',
        'olhando',
        'registradas',
        'registrados',
        'registrada',
        'registrado',
        'escola',
        'colegio',
        'colégio',
        'politica',
        'política',
        'publica',
        'pública',
        'cada',
        'cada um',
        'cada filho',
        'negociar',
        'negociacao',
        'negociação',
        'restante',
        'parcialmente',
        'paga',
        'pago',
        'taxa',
        'desconto',
        'descontos',
        'situacao',
        'situação',
        'financeira',
    }
    phrase_disallow = {
        'cada filho',
        'cada um',
        'meus filhos',
        'dos meus filhos',
        'negociar uma',
        'atendimento com o financeiro',
        'mensalidade parcialmente paga',
        'situacao financeira',
        'situação financeira',
    }
    has_student_context = _is_student_reference_context_message(normalized)
    for pattern, requires_student_context in patterns:
        if requires_student_context and not has_student_context:
            continue
        for match in re.finditer(pattern, normalized):
            raw = match.group(1).strip(' ?!.,;:')
            tokens = [token for token in raw.split() if token not in stopwords]
            if not tokens:
                continue
            if len(tokens) == 1 and tokens[0] in stopwords:
                continue
            trimmed_tokens: list[str] = []
            for token in tokens:
                if token in {
                    'como',
                    'qual',
                    'quais',
                    'quanto',
                    'quantas',
                    'quantos',
                    'que',
                    'serve',
                    'esta',
                    'está',
                    'tem',
                    'fica',
                    'ficou',
                }:
                    break
                trimmed_tokens.append(token)
            if trimmed_tokens:
                tokens = trimmed_tokens
            candidate = ' '.join(tokens[:3]).strip()
            if not candidate:
                continue
            if candidate in phrase_disallow or any(
                candidate.startswith(f'{term} ') for term in phrase_disallow
            ):
                continue
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return candidates


def _looks_like_non_student_followup_candidate(candidate: str) -> bool:
    normalized = _normalize_text(candidate).strip()
    if not normalized:
        return False
    disallowed = {
        'frequencia',
        'frequência',
        'falta',
        'faltas',
        'que falta',
        'o que falta',
        'ok e o que falta',
        'frequencia dele esta',
        'frequência dele está',
        'frequencia dela esta',
        'frequência dela está',
        'esta ok',
        'está ok',
        'nota',
        'notas',
        'boletim',
        'academico',
        'acadêmico',
        'escopo academico',
        'escopo acadêmico',
        'escopo financeiro',
        'financeiro',
        'familia',
        'família',
        'responsavel',
        'responsável',
        'situacao financeira',
        'situação financeira',
        'documentacao',
        'documentação',
        'escopo',
        'historia',
        'história',
        'fisica',
        'física',
        'matematica',
        'matemática',
        'biologia',
        'geografia',
        'quimica',
        'química',
        'portugues',
        'português',
        'ingles',
        'inglês',
        'boletos',
        'contrato',
        'protocolo',
        'visita',
        'atendimento',
        'bloqueando',
        'bloqueio',
        'regular',
        'regularidade',
        'professor',
        'professora',
        'docente',
        'manual',
        'interno',
        'material interno',
        'comunicacao pedagogica',
        'comunicação pedagógica',
        'registro de avaliacoes',
        'registro de avaliações',
        'olhando',
        'faltas registradas',
        'registros recentes',
        'escola',
        'colegio',
        'colégio',
        'politica publica',
        'política pública',
        'bullying',
        'assedio',
        'assédio',
        'agressao',
        'agressão',
        'intimidacao',
        'intimidação',
        'discriminacao',
        'discriminação',
        'bom comportamento',
        'mal comportamento',
        'comportamento',
        'expulsao',
        'expulsão',
        'exclusao',
        'exclusão',
        'bomba',
        'explosivo',
        'explosivos',
        'seguranca',
        'segurança',
        'cada filho',
        'cada um',
        'meus filhos',
        'dos meus filhos',
        'negociar uma',
        'atendimento com o financeiro',
        'mensalidade parcialmente paga',
        'taxa',
        'desconto',
        'descontos',
    }
    if normalized in {_normalize_text(term) for term in disallowed}:
        return True
    if any(_message_matches_term(normalized, term) for term in disallowed):
        return True
    if normalized in SUBJECT_HINTS:
        return True
    return any(
        normalized in {_normalize_text(hint) for hint in hints} for hints in SUBJECT_HINTS.values()
    )


def _student_matches_candidate(student: dict[str, Any], candidate: str) -> bool:
    normalized_candidate = _normalize_text(candidate).strip()
    if not normalized_candidate:
        return False
    full_name = _normalize_text(str(student.get('full_name', '')))
    if not full_name:
        return False
    if normalized_candidate == full_name or normalized_candidate in full_name:
        return True
    return normalized_candidate in _student_name_tokens(student)


def _explicit_unmatched_student_reference(
    students: list[dict[str, Any]],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    if _is_access_scope_query(message) or _is_access_scope_repair_query(
        message, {'linked_students': students}, conversation_context
    ):
        return None
    if match_public_canonical_lane(message):
        return None
    if (
        _looks_like_family_finance_aggregate_query(message)
        or _looks_like_family_attendance_aggregate_query(message)
        or _looks_like_family_academic_aggregate_query(message)
    ):
        return None
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'abrir um atendimento',
            'abre um atendimento',
            'abrir um chamado',
            'abrir um protocolo',
        }
    ) and any(
        _message_matches_term(normalized, term)
        for term in SUPPORT_FINANCE_TERMS | {'negociar', 'mensalidade parcialmente paga'}
    ):
        return None
    candidates = _extract_explicit_student_reference_candidates(message)
    if not candidates and isinstance(conversation_context, dict):
        recent_focus = _recent_trace_focus(conversation_context) or {}
        recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
        recent_student_name = str(
            recent_focus.get('academic_student_name')
            or recent_focus.get('finance_student_name')
            or recent_focus.get('student_name')
            or ''
        ).strip()
        normalized = _normalize_text(message)
        followup_match = re.fullmatch(
            r'(?:e\s+d[oa]|e\s+se\s+eu\s+perguntar\s+d[oa])\s+([a-z]{3,}(?:\s+[a-z]{3,}){0,2})\??',
            normalized,
        )
        if followup_match and (
            recent_active_task.startswith(('academic:', 'finance:', 'admin:'))
            or bool(recent_student_name)
        ):
            followup_candidate = followup_match.group(1).strip()
            if followup_candidate and not _looks_like_non_student_followup_candidate(
                followup_candidate
            ):
                candidates.append(followup_candidate)
    for candidate in candidates:
        if _looks_like_non_student_followup_candidate(candidate):
            continue
        if any(_student_matches_candidate(student, candidate) for student in students):
            continue
        return candidate
    return None


def _format_student_options(students: list[dict[str, Any]]) -> str:
    return ', '.join(
        f'{student.get("full_name", "Aluno")} ({student.get("enrollment_code", "sem codigo")})'
        for student in students
    )


def _compose_unmatched_student_reference_answer(
    *,
    requested_name: str,
    students: list[dict[str, Any]],
) -> str:
    options = _format_student_options(students)
    return (
        f'Hoje eu nao encontrei {requested_name.title()} entre os alunos vinculados a esta conta. '
        f'No momento, os alunos que aparecem aqui sao: {options}. '
        'Se quiser, me diga qual deles voce quer consultar.'
    )


def _matching_students_in_text(students: list[dict[str, Any]], text: str) -> list[dict[str, Any]]:
    matches = {
        str(student.get('student_id')): student
        for student in students
        if _student_matches_text(student, text)
    }
    if matches:
        return list(matches.values())

    normalized_text = _normalize_text(text)
    token_index: dict[str, list[dict[str, Any]]] = {}
    for student in students:
        for token in _student_name_tokens(student):
            token_index.setdefault(token, []).append(student)
    for token, owners in token_index.items():
        if len(owners) == 1 and _message_matches_term(normalized_text, token):
            owner = owners[0]
            matches[str(owner.get('student_id'))] = owner
    return list(matches.values())


def _recent_student_from_context(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    students = _eligible_students(actor, capability=capability)
    if not students or not isinstance(conversation_context, dict):
        return None
    recent_focus = _recent_trace_focus(conversation_context) or {}
    recent_active_task = str(recent_focus.get('active_task', '') or '').strip()
    primary_slot_key = (
        'academic_student_name' if capability == 'academic' else 'finance_student_name'
    )
    secondary_slot_key = (
        'finance_student_name' if capability == 'academic' else 'academic_student_name'
    )
    candidate_names: list[str] = []
    primary_candidate_name = _recent_slot_value(conversation_context, primary_slot_key)
    if primary_candidate_name:
        candidate_names.append(primary_candidate_name)
    same_capability_task = recent_active_task.startswith(f'{capability}:')
    if same_capability_task:
        secondary_candidate_name = _recent_slot_value(conversation_context, secondary_slot_key)
        if secondary_candidate_name and secondary_candidate_name not in candidate_names:
            candidate_names.append(secondary_candidate_name)
    if recent_active_task == 'admin:student_administrative_status':
        active_entity = str(recent_focus.get('active_entity', '') or '').strip()
        if active_entity and active_entity not in candidate_names and active_entity != 'aluno':
            candidate_names.append(active_entity)
    for candidate_name in candidate_names:
        matched_students = _matching_students_in_text(students, candidate_name)
        if len(matched_students) == 1:
            return matched_students[0]
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        matched_students = _matching_students_in_text(students, content)
        if len(matched_students) == 1:
            return matched_students[0]
    if not same_capability_task:
        return None
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        matched_students = _matching_students_in_text(students, content)
        if len(matched_students) == 1:
            return matched_students[0]
    return None


def _student_from_slot_memory(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    slot_memory: ConversationSlotMemory | None,
) -> dict[str, Any] | None:
    students = _eligible_students(actor, capability=capability)
    if not students or slot_memory is None:
        return None
    candidate_names: list[str] = []
    primary_name = (
        slot_memory.academic_student_name
        if capability == 'academic'
        else slot_memory.finance_student_name
    )
    secondary_name = (
        slot_memory.finance_student_name
        if capability == 'academic'
        else slot_memory.academic_student_name
    )
    for candidate_name in (primary_name, secondary_name, slot_memory.active_entity):
        normalized_candidate = str(candidate_name or '').strip()
        if (
            normalized_candidate
            and normalized_candidate not in candidate_names
            and normalized_candidate != 'aluno'
        ):
            candidate_names.append(normalized_candidate)
    for candidate_name in candidate_names:
        matched_students = _matching_students_in_text(students, candidate_name)
        if len(matched_students) == 1:
            return matched_students[0]
    return None


def _focus_marked_student_from_message(
    students: list[dict[str, Any]],
    message: str,
) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    positive_markers = (
        'so ',
        'só ',
        'apenas ',
        'somente ',
        'so a ',
        'só a ',
        'so o ',
        'só o ',
        'olhe so para ',
        'olhe só para ',
        'agora foque so na ',
        'agora foque só na ',
        'foque so na ',
        'foque só na ',
        'fique apenas com ',
        'fique só com ',
        'recorte so ',
        'recorte só ',
        'isole a ',
        'isole o ',
        'corta so para ',
        'corta só para ',
        'corta so para a ',
        'corta só para a ',
        'corta so para o ',
        'corta só para o ',
        'filtre apenas ',
        'agora quero apenas ',
        'agora quero so ',
        'agora quero só ',
    )
    for student in students:
        full_name = str(student.get('full_name') or '').strip()
        if not full_name:
            continue
        normalized_full_name = _normalize_text(full_name)
        first_name = normalized_full_name.split(' ')[0] if normalized_full_name else ''
        candidate_forms = tuple(value for value in {normalized_full_name, first_name} if value)
        if not candidate_forms:
            continue
        for candidate in candidate_forms:
            for marker in positive_markers:
                if f'{marker}{candidate}' in normalized:
                    return student
            if re.search(
                rf'\b(?:so|só|apenas|somente)\s+(?:a|o)\s+{re.escape(candidate)}\b', normalized
            ):
                return student
    return None


def _recent_multi_student_summary_context(
    actor: dict[str, Any] | None,
    *,
    conversation_context: dict[str, Any] | None,
) -> bool:
    students = _linked_students(actor)
    if len(students) <= 1 or not isinstance(conversation_context, dict):
        return False
    recent_assistant = next(
        (
            content
            for sender_type, content in reversed(_recent_message_lines(conversation_context))
            if sender_type == 'assistant' and str(content or '').strip()
        ),
        '',
    )
    if not recent_assistant:
        return False
    normalized = _normalize_text(recent_assistant)
    if (
        'resumo financeiro das contas vinculadas' in normalized
        or 'mais de um aluno vinculado' in normalized
    ):
        return True
    mentioned = 0
    for student in students:
        full_name = _normalize_text(str(student.get('full_name', '') or ''))
        if full_name and full_name in normalized:
            mentioned += 1
    return mentioned >= 2


def _select_linked_student(
    actor: dict[str, Any] | None,
    message: str,
    *,
    capability: str = 'academic',
    conversation_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    students = _eligible_students(actor, capability=capability)
    if not students:
        return None, 'Nao encontrei um aluno vinculado a esta conta para essa consulta.'

    matched_students = _matching_students_in_text(students, message)
    if len(matched_students) == 1:
        return matched_students[0], None
    focus_marked_student = _focus_marked_student_from_message(students, message)
    if focus_marked_student is not None:
        return focus_marked_student, None

    recent_student = _recent_student_from_context(
        actor,
        capability=capability,
        conversation_context=conversation_context,
    )

    unmatched_student_reference = _explicit_unmatched_student_reference(
        students,
        message,
        conversation_context=conversation_context,
    )
    if unmatched_student_reference and recent_student is not None:
        unmatched_tokens = _normalize_text(unmatched_student_reference).split()
        recent_tokens = set(_student_name_tokens(recent_student))
        if (
            unmatched_tokens
            and unmatched_tokens[0] in recent_tokens
            and _is_follow_up_query(message)
        ):
            unmatched_student_reference = None
            if not _recent_multi_student_summary_context(
                actor, conversation_context=conversation_context
            ):
                return recent_student, None
    if unmatched_student_reference:
        return None, _compose_unmatched_student_reference_answer(
            requested_name=unmatched_student_reference,
            students=students,
        )

    if len(students) == 1:
        return students[0], None

    if (
        recent_student is not None
        and _is_follow_up_query(message)
        and not _recent_multi_student_summary_context(
            actor, conversation_context=conversation_context
        )
    ):
        return recent_student, None

    options = _format_student_options(students)
    return (
        None,
        f'Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: {options}.',
    )
