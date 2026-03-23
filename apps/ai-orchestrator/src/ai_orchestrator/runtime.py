from __future__ import annotations

import unicodedata
from datetime import date, timedelta
from typing import Any

import httpx
from openai import AsyncOpenAI

from .graph import build_orchestration_graph, to_preview
from .models import (
    CalendarEventCard,
    MessageResponse,
    MessageResponseCitation,
    MessageResponseRequest,
    OrchestrationMode,
    OrchestrationRequest,
    QueryDomain,
    RetrievalBackend,
    UserContext,
    UserRole,
)
from .retrieval import get_retrieval_service


DEFAULT_PUBLIC_HELP = (
    'Posso ajudar com informacoes publicas da escola, como calendario, matricula, '
    'documentos exigidos e regras de atendimento digital.'
)

ATTENDANCE_TERMS = {'frequencia', 'falta', 'faltas', 'presenca', 'presencas'}
GRADE_TERMS = {'nota', 'notas', 'boletim', 'avaliacao', 'avaliacoes', 'prova', 'provas'}
TEACHER_SCHEDULE_TERMS = {'horario', 'grade', 'agenda', 'turma', 'turmas', 'aula', 'aulas'}


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.lower()


def _map_request(request: MessageResponseRequest, user_context: UserContext) -> OrchestrationRequest:
    return OrchestrationRequest(
        message=request.message,
        conversation_id=request.conversation_id,
        user=user_context,
        allow_graph_rag=request.allow_graph_rag,
        allow_handoff=request.allow_handoff,
    )


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
    return any(term in lowered for term in terms)


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


async def _api_core_get(
    *,
    settings: Any,
    path: str,
    params: dict[str, object] | None = None,
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(f'{settings.api_core_url}{path}', params=params, headers=headers)
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict):
            return payload, response.status_code
        return None, response.status_code
    except httpx.HTTPStatusError as exc:
        return None, exc.response.status_code
    except Exception:
        return None, None


async def _fetch_actor_context(*, settings: Any, telegram_chat_id: int | None) -> dict[str, Any] | None:
    if telegram_chat_id is None:
        return None
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/internal/identity/context',
        params={'telegram_chat_id': telegram_chat_id},
    )
    if status_code != 200 or payload is None:
        return None
    actor = payload.get('actor')
    return actor if isinstance(actor, dict) else None


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


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not actor:
        return []
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _select_linked_student(actor: dict[str, Any] | None, message: str) -> tuple[dict[str, Any] | None, str | None]:
    students = _linked_students(actor)
    if not students:
        return None, 'Nao encontrei um aluno vinculado a esta conta para essa consulta.'

    if len(students) == 1:
        return students[0], None

    normalized_message = _normalize_text(message)
    matches: list[dict[str, Any]] = []
    for student in students:
        full_name = str(student.get('full_name', ''))
        enrollment_code = str(student.get('enrollment_code', ''))
        normalized_name = _normalize_text(full_name)
        if normalized_name and normalized_name in normalized_message:
            matches.append(student)
            continue
        if enrollment_code and enrollment_code.lower() in normalized_message:
            matches.append(student)

    unique_matches = {str(item.get('student_id')): item for item in matches}
    if len(unique_matches) == 1:
        return next(iter(unique_matches.values())), None

    options = ', '.join(
        f"{student.get('full_name', 'Aluno')} ({student.get('enrollment_code', 'sem codigo')})"
        for student in students
    )
    return None, f'Sua conta tem mais de um aluno vinculado. Diga qual aluno deseja consultar: {options}.'


def _format_grades(summary: dict[str, Any]) -> list[str]:
    grades = summary.get('grades')
    if not isinstance(grades, list) or not grades:
        return ['- Ainda nao ha lancamentos de notas no periodo consultado.']
    lines = []
    for grade in grades[:4]:
        if not isinstance(grade, dict):
            continue
        lines.append(
            '- {subject_name} - {item_title}: {score}/{max_score}'.format(
                subject_name=grade.get('subject_name', 'Disciplina'),
                item_title=grade.get('item_title', 'Atividade'),
                score=grade.get('score', '?'),
                max_score=grade.get('max_score', '?'),
            )
        )
    return lines or ['- Ainda nao ha lancamentos de notas no periodo consultado.']


def _format_attendance(summary: dict[str, Any]) -> list[str]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list) or not attendance:
        return ['- Ainda nao ha registros consolidados de frequencia.']
    lines = []
    for row in attendance[:4]:
        if not isinstance(row, dict):
            continue
        lines.append(
            '- {subject_name}: {present} presencas, {late} atrasos, {absent} faltas ({minutes} min)'.format(
                subject_name=row.get('subject_name', 'Disciplina'),
                present=row.get('present_count', 0),
                late=row.get('late_count', 0),
                absent=row.get('absent_count', 0),
                minutes=row.get('absent_minutes', 0),
            )
        )
    return lines or ['- Ainda nao ha registros consolidados de frequencia.']


def _format_invoices(summary: dict[str, Any]) -> list[str]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list) or not invoices:
        return ['- Nenhuma fatura encontrada para o contrato atual.']
    lines = []
    for invoice in invoices[:4]:
        if not isinstance(invoice, dict):
            continue
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=invoice.get('status', 'desconhecido'),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines or ['- Nenhuma fatura encontrada para o contrato atual.']


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


def _compose_structured_deny(actor: dict[str, Any] | None) -> str:
    if actor is None:
        return (
            'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
            'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando '
            '`/start link_<codigo>` ao bot.'
        )
    return 'Nao consegui autorizar essa consulta neste contexto. Se precisar, use o portal autenticado da escola.'


async def _compose_structured_tool_answer(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
) -> str:
    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    actor = actor or await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if actor is None:
        return _compose_structured_deny(actor)

    role_code = str(actor.get('role_code', 'anonymous'))
    message = request.message

    if preview.classification.domain is QueryDomain.academic and role_code == 'teacher':
        if not _contains_any(message, TEACHER_SCHEDULE_TERMS):
            return (
                'No Telegram, o fluxo protegido do professor nesta etapa cobre horario e turmas. '
                'Pergunte por exemplo: "qual meu horario?" ou "quais sao minhas turmas?".'
            )
        payload, status_code = await _api_core_get(
            settings=settings,
            path='/v1/teachers/me/schedule',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar sua grade docente agora. Tente novamente em instantes.'
        summary = payload.get('summary', {})
        teacher_name = summary.get('teacher_name', actor.get('full_name', 'Professor'))
        assignments = _format_assignments(summary if isinstance(summary, dict) else {})
        return '\n'.join([f'Grade docente de {teacher_name}:', *assignments])

    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        student, clarification = _select_linked_student(actor, message)
        if clarification is not None:
            return clarification
        if student is None:
            return 'Nao encontrei um aluno elegivel para essa consulta no Telegram.'

        student_id = student.get('student_id')
        student_name = student.get('full_name', 'Aluno')
        if not isinstance(student_id, str):
            return 'Nao consegui identificar o aluno desta consulta. Tente novamente pelo portal.'

        if preview.classification.domain is QueryDomain.academic:
            payload, status_code = await _api_core_get(
                settings=settings,
                path=f'/v1/students/{student_id}/academic-summary',
                params={'telegram_chat_id': request.telegram_chat_id},
            )
            if status_code == 403:
                return 'Seu perfil nao tem permissao para consultar esses dados academicos.'
            if status_code != 200 or payload is None:
                return 'Nao consegui consultar os dados academicos agora. Tente novamente em instantes.'

            summary = payload.get('summary', {})
            if not isinstance(summary, dict):
                return 'Nao consegui interpretar o retorno academico desta consulta.'

            focus_attendance = _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS)
            lines = [
                f'Resumo academico de {student_name}:',
                f"- Turma: {summary.get('class_name', 'nao informada')}",
                f"- Serie atual: {summary.get('grade_level', 'nao informada')}",
            ]
            if focus_attendance:
                lines.append('Frequencia:')
                lines.extend(_format_attendance(summary))
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(summary))
            else:
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(summary))
                lines.append('Frequencia:')
                lines.extend(_format_attendance(summary))
            return '\n'.join(lines)

        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/financial-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code == 403:
            return 'Seu perfil nao tem permissao para consultar esses dados financeiros.'
        if status_code != 200 or payload is None:
            return 'Nao consegui consultar o resumo financeiro agora. Tente novamente em instantes.'

        summary = payload.get('summary', {})
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno financeiro desta consulta.'

        lines = [
            f"Resumo financeiro de {summary.get('student_name', student_name)}:",
            f"- Contrato: {summary.get('contract_code', 'nao informado')}",
            f"- Responsavel financeiro: {summary.get('guardian_name', 'nao informado')}",
            f"- Mensalidade base: {summary.get('monthly_amount', '0.00')}",
            f"- Faturas em aberto: {summary.get('open_invoice_count', 0)}",
            f"- Faturas vencidas: {summary.get('overdue_invoice_count', 0)}",
            'Ultimas faturas:',
            *_format_invoices(summary),
        ]
        return '\n'.join(lines)

    return (
        'Esse fluxo protegido ainda nao foi concluido para este perfil no Telegram. '
        'Por enquanto, use o portal autenticado da escola.'
    )


def _compose_deterministic_answer(
    *,
    preview: Any,
    retrieval_hits: list[Any],
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str:
    if preview.mode is OrchestrationMode.deny:
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

    if preview.classification.domain is QueryDomain.calendar and calendar_events:
        sections.append('Encontrei estes proximos eventos publicos no calendario escolar:')
        sections.extend(_format_event_line(event) for event in calendar_events[:3])

    if retrieval_hits:
        intro = 'Segundo a base institucional atual:'
        if preview.classification.domain is QueryDomain.calendar and sections:
            intro = 'Tambem localizei estas referencias na base documental:'
        sections.append(intro)
        sections.extend(f'- {hit.text_excerpt}' for hit in retrieval_hits[:2])

    if not sections:
        return (
            'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
            'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
        )

    source_lines = _render_source_lines(citations)
    if source_lines:
        sections.append(source_lines)
    return '\n'.join(sections)


async def _compose_with_openai(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    citations: list[MessageResponseCitation],
    calendar_events: list[CalendarEventCard],
) -> str | None:
    if settings.llm_provider != 'openai' or not settings.openai_api_key:
        return None

    snippets = '\n\n'.join(
        f'Fonte {index}: {citation.document_title} ({citation.version_label})\nTrecho: {citation.excerpt}'
        for index, citation in enumerate(citations, start=1)
    )
    calendar_context = '\n'.join(_format_event_line(event) for event in calendar_events[:4])

    instructions = (
        'Voce e o assistente EduAssist de uma escola de ensino medio. '
        'Responda em portugues do Brasil, de forma objetiva e educada. '
        'Use apenas o contexto fornecido. Nao invente regras, datas ou documentos. '
        'Se a pergunta exigir autenticacao, diga isso com clareza. '
        'Se houver calendario estruturado, priorize-o. Nao cite fontes inline; elas serao anexadas depois.'
    )
    prompt = (
        f'Pergunta do usuario:\n{request.message}\n\n'
        f'Roteamento:\n- modo: {preview.mode.value}\n'
        f'- dominio: {preview.classification.domain.value}\n'
        f'- autenticacao necessaria: {preview.needs_authentication}\n\n'
        f'Eventos estruturados:\n{calendar_context or "nenhum"}\n\n'
        f'Trechos citaveis:\n{snippets or "nenhum"}'
    )

    try:
        client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)
        response = await client.responses.create(
            model=settings.openai_model,
            instructions=instructions,
            input=prompt,
        )
        text = (response.output_text or '').strip()
        if not text:
            return None
        return text
    except Exception:
        return None


async def generate_message_response(*, request: MessageResponseRequest, settings: Any) -> MessageResponse:
    actor = await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    effective_user = _user_context_from_actor(actor) if actor else request.user

    graph = build_orchestration_graph(settings.graph_rag_enabled)
    state = graph.invoke({'request': _map_request(request, effective_user)})
    preview = to_preview(state)

    retrieval_hits: list[Any] = []
    citations: list[MessageResponseCitation] = []
    calendar_events: list[CalendarEventCard] = []

    if preview.mode is OrchestrationMode.hybrid_retrieval:
        retrieval_service = get_retrieval_service(
            database_url=settings.database_url,
            qdrant_url=settings.qdrant_url,
            collection_name=settings.qdrant_documents_collection,
            embedding_model=settings.document_embedding_model,
        )
        search = retrieval_service.hybrid_search(
            query=request.message,
            top_k=4,
            visibility='public',
            category=_category_for_domain(preview.classification.domain),
        )
        retrieval_hits = search.hits
        citations = _collect_citations(search.hits)

        if preview.classification.domain is QueryDomain.calendar:
            calendar_events = await _fetch_public_calendar(settings=settings)

    if preview.mode is OrchestrationMode.structured_tool:
        message_text = await _compose_structured_tool_answer(
            settings=settings,
            request=request,
            preview=preview,
            actor=actor,
        )
    else:
        llm_text = await _compose_with_openai(
            settings=settings,
            request=request,
            preview=preview,
            citations=citations,
            calendar_events=calendar_events,
        )
        message_text = llm_text or _compose_deterministic_answer(
            preview=preview,
            retrieval_hits=retrieval_hits,
            citations=citations,
            calendar_events=calendar_events,
        )

    if citations:
        sources = _render_source_lines(citations)
        if sources and sources not in message_text:
            message_text = f'{message_text}\n\n{sources}'

    return MessageResponse(
        message_text=message_text,
        mode=preview.mode,
        classification=preview.classification,
        retrieval_backend=preview.retrieval_backend,
        selected_tools=preview.selected_tools,
        citations=citations,
        calendar_events=calendar_events,
        needs_authentication=preview.needs_authentication,
        graph_path=preview.graph_path,
        risk_flags=preview.risk_flags,
        reason=preview.reason,
    )
