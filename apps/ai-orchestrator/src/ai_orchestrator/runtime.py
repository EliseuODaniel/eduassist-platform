from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta
from time import monotonic
from typing import Any

import httpx
from eduassist_observability import record_counter, record_histogram, set_span_attributes, start_span

from .graph_rag_runtime import graph_rag_workspace_ready, run_graph_rag_query
from .llm_provider import compose_with_provider
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
TEACHER_SCHEDULE_TERMS = {
    'horario',
    'grade',
    'agenda',
    'turma',
    'turmas',
    'aula',
    'aulas',
    'disciplina',
    'disciplinas',
    'materia',
    'materias',
}
TEACHER_CLASS_TERMS = {'turma', 'turmas', 'classe', 'classes'}
TEACHER_SUBJECT_TERMS = {'disciplina', 'disciplinas', 'materia', 'materias'}
FINANCE_OPEN_TERMS = {'aberto', 'abertos', 'em aberto', 'pendencia', 'pendencias', 'boleto', 'boletos'}
FINANCE_OVERDUE_TERMS = {'vencido', 'vencidos', 'vencida', 'vencidas', 'atrasado', 'atrasados', 'inadimplencia'}
FINANCE_PAID_TERMS = {
    'pago',
    'pagos',
    'paga',
    'pagas',
    'quitado',
    'quitados',
    'quitada',
    'quitadas',
    'pagamento',
    'pagamentos',
}
FINANCE_SECOND_COPY_TERMS = {'segunda via', '2a via', 'boleto', 'boletos'}
SUBJECT_HINTS = {
    'matematica': {'matematica'},
    'portugues': {'portugues', 'redacao'},
    'biologia': {'biologia', 'bio'},
}
SUPPORT_FINANCE_TERMS = {'financeiro', 'boleto', 'mensalidade', 'pagamento', 'fatura', 'faturas'}
SUPPORT_COORDINATION_TERMS = {'coordenacao', 'pedagogico', 'ocorrencia', 'professor', 'disciplina'}
SUPPORT_SECRETARIAT_TERMS = {'secretaria', 'matricula', 'documento', 'declaracao', 'historico', 'transferencia'}
PUBLIC_ENTITY_HINTS = {
    'biblioteca': 'biblioteca',
    'cantina': 'cantina',
    'laboratorio': 'laboratorio',
    'laboratorio de ciencias': 'laboratorio',
    'secretaria': 'secretaria',
    'portaria': 'portaria',
}
PROMPT_DISCLOSURE_TERMS = {
    'prompt',
    'system prompt',
    'prompt do sistema',
    'prompt de sistema',
    'instrucoes internas',
    'instrucoes ocultas',
    'ocultas do sistema',
    'agents.md',
    'policy.rego',
}
PROMPT_BYPASS_TERMS = {
    'ignore todas as instrucoes',
    'ignore as instrucoes',
    'revele',
    'divulgue',
    'mostre o prompt',
    'me diga o prompt',
}
NEGATIVE_REQUIREMENT_TERMS = {
    'nao preciso',
    'nao precisa',
    'nao e necessario',
    'nao sao necessarios',
    'nao sao necessarias',
    'dispensavel',
    'dispensaveis',
    'dispensado',
    'dispensados',
    'exceto',
}
REQUIREMENT_QUERY_TERMS = {'documento', 'documentos', 'matricula'}
KNOWN_ADMISSIONS_REQUIREMENTS = [
    'ficha cadastral ou formulario cadastral preenchido',
    'documento de identificacao do aluno',
    'CPF do aluno, quando houver',
    'historico escolar',
    'comprovante de residencia',
    'documento de identificacao do responsavel legal',
]


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


def _extract_public_entity_hints(message: str) -> set[str]:
    lowered = _normalize_text(message)
    return {canonical for term, canonical in PUBLIC_ENTITY_HINTS.items() if term in lowered}


def _is_prompt_disclosure_probe(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(term in normalized for term in PROMPT_DISCLOSURE_TERMS) or any(
        term in normalized for term in PROMPT_BYPASS_TERMS
    )


def _is_negative_requirement_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_negative = any(term in normalized for term in NEGATIVE_REQUIREMENT_TERMS)
    has_requirement = any(term in normalized for term in REQUIREMENT_QUERY_TERMS)
    return has_negative and has_requirement


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


def _compose_negative_requirement_answer() -> str:
    lines = [
        'A base atual informa os documentos exigidos para a matricula, mas nao lista explicitamente quais documentos sao dispensaveis.',
        'Por isso, nao e seguro afirmar o que voce "nao precisa" levar.',
        'O que esta explicitamente exigido hoje e:',
    ]
    lines.extend(f'- {item}' for item in KNOWN_ADMISSIONS_REQUIREMENTS)
    lines.append('Se quiser, eu posso resumir apenas os documentos exigidos ou explicar as etapas da matricula.')
    return '\n'.join(lines)


def _retrieval_hits_cover_query_hints(retrieval_hits: list[Any], query_hints: set[str]) -> bool:
    if not query_hints:
        return True
    if not retrieval_hits:
        return False

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
    return all(hint in haystack for hint in query_hints)


def _filter_retrieval_hits_by_query_hints(retrieval_hits: list[Any], query_hints: set[str]) -> list[Any]:
    if not query_hints:
        return retrieval_hits

    filtered_hits = []
    for hit in retrieval_hits:
        haystack = _normalize_text(
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
        if any(hint in haystack for hint in query_hints):
            filtered_hits.append(hit)
    return filtered_hits or retrieval_hits


def _compose_public_gap_answer(query_hints: set[str]) -> str:
    if query_hints:
        labels = ', '.join(sorted(query_hints))
        return (
            f'Ainda nao encontrei uma resposta suficientemente suportada na base publica sobre {labels}. '
            'Se esse servico existir, preciso que a base documental seja atualizada ou que voce reformule a pergunta '
            'com o nome oficial do setor.'
        )
    return (
        'Ainda nao encontrei uma resposta suficientemente suportada na base publica. '
        'Tente reformular a pergunta com termos como matricula, calendario, secretaria ou atendimento.'
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


async def _api_core_get(
    *,
    settings: Any,
    path: str,
    params: dict[str, object] | None = None,
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {'X-Internal-Api-Token': settings.internal_api_token}
    with start_span(
        'eduassist.api_core.get',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_params': bool(params),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.get(f'{settings.api_core_url}{path}', params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(payload, dict):
                return payload, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
            return None, exc.response.status_code
        except Exception:
            return None, None


async def _api_core_post(
    *,
    settings: Any,
    path: str,
    payload: dict[str, object],
) -> tuple[dict[str, Any] | None, int | None]:
    headers = {
        'X-Internal-Api-Token': settings.internal_api_token,
        'Content-Type': 'application/json',
    }
    with start_span(
        'eduassist.api_core.post',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.api_core.path': path,
            'eduassist.api_core.has_payload': bool(payload),
        },
    ):
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                response = await client.post(f'{settings.api_core_url}{path}', json=payload, headers=headers)
            response.raise_for_status()
            body = response.json()
            set_span_attributes(**{'http.status_code': response.status_code})
            if isinstance(body, dict):
                return body, response.status_code
            return None, response.status_code
        except httpx.HTTPStatusError as exc:
            set_span_attributes(**{'http.status_code': exc.response.status_code})
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


async def _fetch_public_school_profile(*, settings: Any) -> dict[str, Any] | None:
    payload, status_code = await _api_core_get(
        settings=settings,
        path='/v1/public/school-profile',
    )
    if status_code != 200 or payload is None:
        return None
    profile = payload.get('profile')
    return profile if isinstance(profile, dict) else None


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

    return f'{requester} solicitou apoio humano pelo canal {request.channel.value}: {message_excerpt}'


async def _create_support_handoff(
    *,
    settings: Any,
    request: MessageResponseRequest,
    actor: dict[str, Any] | None,
) -> dict[str, Any] | None:
    conversation_external_id = request.conversation_id
    if not conversation_external_id:
        conversation_external_id = f'{request.channel.value}:{request.telegram_chat_id or "anonymous"}:handoff'

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


def _compose_handoff_answer(handoff_payload: dict[str, Any] | None) -> str:
    if not handoff_payload:
        return (
            'Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o '
            'encaminhamento humano agora. Tente novamente em instantes ou use a secretaria.'
        )

    item = handoff_payload.get('item')
    if not isinstance(item, dict):
        return (
            'Registrei a necessidade de atendimento humano, mas nao consegui recuperar o protocolo. '
            'Use a secretaria para confirmar a fila.'
        )

    queue_name = str(item.get('queue_name', 'atendimento'))
    ticket_code = str(item.get('ticket_code', 'protocolo indisponivel'))
    status = str(item.get('status', 'queued'))
    created = bool(handoff_payload.get('created', False))

    if created:
        return (
            f'Encaminhei sua solicitacao para a fila de {queue_name}. '
            f'Protocolo: {ticket_code}. Status atual: {status}. '
            'A equipe humana podera continuar esse atendimento no portal operacional.'
        )

    return (
        f'Sua solicitacao ja estava registrada na fila de {queue_name}. '
        f'Protocolo: {ticket_code}. Status atual: {status}.'
    )


def _linked_students(actor: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not actor:
        return []
    linked_students = actor.get('linked_students')
    if not isinstance(linked_students, list):
        return []
    return [student for student in linked_students if isinstance(student, dict)]


def _eligible_students(actor: dict[str, Any] | None, *, capability: str) -> list[dict[str, Any]]:
    students = _linked_students(actor)
    if capability == 'academic':
        return [student for student in students if bool(student.get('can_view_academic', False))]
    if capability == 'finance':
        return [student for student in students if bool(student.get('can_view_finance', False))]
    return students


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


def _detect_subject_filter(message: str, summary: dict[str, Any]) -> str | None:
    lowered = _normalize_text(message)
    available_subjects: dict[str, str] = {}

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

    for normalized_subject in available_subjects:
        if normalized_subject in lowered:
            return normalized_subject
        for hint in SUBJECT_HINTS.get(normalized_subject, set()):
            if hint in lowered:
                return normalized_subject

    return None


def _filter_grade_rows(summary: dict[str, Any], *, subject_filter: str | None, term_filter: str | None) -> list[dict[str, Any]]:
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


def _filter_attendance_rows(summary: dict[str, Any], *, subject_filter: str | None) -> list[dict[str, Any]]:
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


def _filter_invoice_rows(summary: dict[str, Any], *, status_filter: set[str] | None) -> list[dict[str, Any]]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list):
        return []
    if not status_filter:
        return [invoice for invoice in invoices if isinstance(invoice, dict)]
    filtered: list[dict[str, Any]] = []
    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue
        status = str(invoice.get('status', '')).lower()
        if status in status_filter:
            filtered.append(invoice)
    return filtered


def _detect_finance_status_filter(message: str) -> set[str] | None:
    lowered = _normalize_text(message)
    if any(term in lowered for term in FINANCE_OVERDUE_TERMS):
        return {'overdue'}
    if any(term in lowered for term in FINANCE_PAID_TERMS):
        return {'paid'}
    if any(term in lowered for term in FINANCE_OPEN_TERMS):
        return {'open', 'overdue'}
    return None


def _format_invoice_lines(invoices: list[dict[str, Any]]) -> list[str]:
    if not invoices:
        return ['- Nenhuma fatura compativel com esse filtro foi encontrada.']
    lines = []
    for invoice in invoices[:6]:
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=invoice.get('status', 'desconhecido'),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines


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
    if preview.classification.domain is QueryDomain.institution:
        profile = await _fetch_public_school_profile(settings=settings)
        if profile is None:
            return _compose_public_gap_answer(set())

        school_name = str(profile.get('school_name', 'a escola'))
        normalized_message = _normalize_text(request.message)
        city = str(profile.get('city', ''))
        state = str(profile.get('state', ''))
        if 'cidade' in normalized_message or 'estado' in normalized_message:
            location = ', '.join(part for part in [city, state] if part)
            if location:
                return f'O nome oficial da escola e {school_name}. Ela esta cadastrada em {location}.'
        return f'O nome oficial da escola e {school_name}.'

    if request.telegram_chat_id is None:
        return _compose_structured_deny(actor)

    actor = actor or await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
    if actor is None:
        return _compose_structured_deny(actor)

    role_code = str(actor.get('role_code', 'anonymous'))
    message = request.message
    normalized_message = _normalize_text(message)

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
        if not isinstance(summary, dict):
            return 'Nao consegui interpretar o retorno da grade docente.'

        if _contains_any(message, TEACHER_CLASS_TERMS) and not _contains_any(message, TEACHER_SUBJECT_TERMS):
            lines = [f'Turmas de {teacher_name}:', *_format_unique_classes(summary)]
            return '\n'.join(lines)

        if _contains_any(message, TEACHER_SUBJECT_TERMS) and not _contains_any(message, TEACHER_CLASS_TERMS):
            lines = [f'Disciplinas de {teacher_name}:', *_format_unique_subjects(summary)]
            return '\n'.join(lines)

        assignments = _format_assignments(summary)
        lines = [f'Grade docente de {teacher_name}:', *assignments]
        if 'horario' in normalized_message or 'agenda' in normalized_message:
            lines.append(
                'Nesta base mockada atual, o detalhamento por bloco de horario ainda nao foi modelado; '
                'por enquanto eu mostro suas alocacoes de turmas e disciplinas.'
            )
        return '\n'.join(lines)

    if preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}:
        if preview.classification.domain is QueryDomain.finance:
            requested_status = _detect_finance_status_filter(message)
            if len(_eligible_students(actor, capability='finance')) > 1:
                student, clarification = _select_linked_student(actor, message)
                if student is None and clarification is not None:
                    summaries: list[dict[str, Any]] = []
                    for candidate in _eligible_students(actor, capability='finance'):
                        candidate_id = candidate.get('student_id')
                        if not isinstance(candidate_id, str):
                            continue
                        payload, status_code = await _api_core_get(
                            settings=settings,
                            path=f'/v1/students/{candidate_id}/financial-summary',
                            params={'telegram_chat_id': request.telegram_chat_id},
                        )
                        if status_code == 200 and isinstance(payload, dict):
                            summary = payload.get('summary')
                            if isinstance(summary, dict):
                                summaries.append(summary)

                    if summaries and not any(
                        _normalize_text(str(student.get('full_name', ''))) in normalized_message
                        for student in _eligible_students(actor, capability='finance')
                    ):
                        lines = ['Panorama financeiro das contas vinculadas:']
                        total_open = 0
                        total_overdue = 0
                        for summary in summaries:
                            open_count = int(summary.get('open_invoice_count', 0) or 0)
                            overdue_count = int(summary.get('overdue_invoice_count', 0) or 0)
                            total_open += open_count
                            total_overdue += overdue_count
                            filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
                            status_line = (
                                f"- {summary.get('student_name', 'Aluno')}: "
                                f"{open_count} em aberto, {overdue_count} vencidas"
                            )
                            lines.append(status_line)
                            for invoice_line in _format_invoice_lines(filtered_invoices)[:2]:
                                lines.append(f'  {invoice_line[2:]}' if invoice_line.startswith('- ') else invoice_line)
                        lines.insert(1, f'- Total de faturas em aberto: {total_open}')
                        lines.insert(2, f'- Total de faturas vencidas: {total_overdue}')
                        if any(term in normalized_message for term in FINANCE_SECOND_COPY_TERMS):
                            lines.append(
                                'A emissao automatica de segunda via ainda entra na proxima etapa; '
                                'por enquanto eu consigo informar a situacao das faturas.'
                            )
                        return '\n'.join(lines)

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

            term_filter = _extract_term_filter(message)
            subject_filter = _detect_subject_filter(message, summary)
            filtered_grades = _filter_grade_rows(summary, subject_filter=subject_filter, term_filter=term_filter)
            filtered_attendance = _filter_attendance_rows(summary, subject_filter=subject_filter)
            filtered_summary = dict(summary)
            filtered_summary['grades'] = filtered_grades
            filtered_summary['attendance'] = filtered_attendance

            focus_attendance = _contains_any(message, ATTENDANCE_TERMS) and not _contains_any(message, GRADE_TERMS)
            lines = [
                f'Resumo academico de {student_name}:',
                f"- Turma: {summary.get('class_name', 'nao informada')}",
                f"- Serie atual: {summary.get('grade_level', 'nao informada')}",
            ]
            if subject_filter:
                lines.append(f"- Disciplina filtrada: {subject_filter.title()}")
            if term_filter:
                lines.append(f'- Bimestre filtrado: {term_filter[-1]}')
            if focus_attendance:
                lines.append('Frequencia:')
                lines.extend(_format_attendance(filtered_summary))
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(filtered_summary))
            else:
                lines.append('Notas mais recentes:')
                lines.extend(_format_grades(filtered_summary))
                lines.append('Frequencia:')
                lines.extend(_format_attendance(filtered_summary))
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

        requested_status = _detect_finance_status_filter(message)
        filtered_invoices = _filter_invoice_rows(summary, status_filter=requested_status)
        lines = [
            f"Resumo financeiro de {summary.get('student_name', student_name)}:",
            f"- Contrato: {summary.get('contract_code', 'nao informado')}",
            f"- Responsavel financeiro: {summary.get('guardian_name', 'nao informado')}",
            f"- Mensalidade base: {summary.get('monthly_amount', '0.00')}",
            f"- Faturas em aberto: {summary.get('open_invoice_count', 0)}",
            f"- Faturas vencidas: {summary.get('overdue_invoice_count', 0)}",
        ]
        if requested_status == {'paid'}:
            lines.append('Faturas pagas:')
        elif requested_status == {'overdue'}:
            lines.append('Faturas vencidas:')
        elif requested_status == {'open', 'overdue'}:
            lines.append('Faturas em aberto ou vencidas:')
        else:
            lines.append('Ultimas faturas:')
        lines.extend(_format_invoice_lines(filtered_invoices))
        if any(term in normalized_message for term in FINANCE_SECOND_COPY_TERMS):
            lines.append(
                'A emissao automatica de segunda via ainda entra na proxima etapa; '
                'por enquanto eu consigo informar a situacao e os vencimentos.'
            )
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
    query_hints: set[str],
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
        return _compose_public_gap_answer(query_hints)

    source_lines = _render_source_lines(citations)
    if source_lines:
        sections.append(source_lines)
    return '\n'.join(sections)


async def generate_message_response(*, request: MessageResponseRequest, settings: Any) -> MessageResponse:
    started_at = monotonic()
    with start_span(
        'eduassist.orchestration.message_response',
        tracer_name='eduassist.ai_orchestrator.runtime',
        **{
            'eduassist.channel': request.channel.value,
            'eduassist.request.message_length': len(request.message),
            'eduassist.request.has_telegram_chat': request.telegram_chat_id is not None,
            'eduassist.orchestration.allow_graph_rag': request.allow_graph_rag,
            'eduassist.orchestration.allow_handoff': request.allow_handoff,
        },
    ):
        actor = await _fetch_actor_context(settings=settings, telegram_chat_id=request.telegram_chat_id)
        effective_user = _user_context_from_actor(actor) if actor else request.user
        set_span_attributes(
            **{
                'eduassist.actor.role': effective_user.role.value,
                'eduassist.actor.authenticated': effective_user.authenticated,
                'eduassist.actor.linked_student_count': len(effective_user.linked_student_ids),
            }
        )

        graph = build_orchestration_graph(settings.graph_rag_enabled)
        with start_span('eduassist.orchestration.graph_preview', tracer_name='eduassist.ai_orchestrator.runtime'):
            state = graph.invoke({'request': _map_request(request, effective_user)})
            preview = to_preview(state)
        set_span_attributes(
            **{
                'eduassist.orchestration.mode': preview.mode.value,
                'eduassist.orchestration.domain': preview.classification.domain.value,
                'eduassist.orchestration.access_tier': preview.classification.access_tier.value,
                'eduassist.orchestration.needs_authentication': preview.needs_authentication,
                'eduassist.orchestration.selected_tools': preview.selected_tools,
                'eduassist.orchestration.graph_path': preview.graph_path,
                'eduassist.orchestration.retrieval_backend': preview.retrieval_backend.value,
            }
        )

        retrieval_hits: list[Any] = []
        citations: list[MessageResponseCitation] = []
        calendar_events: list[CalendarEventCard] = []
        query_hints: set[str] = set()
        retrieval_supported = True
        graph_rag_answer: dict[str, str] | None = None

        if preview.mode is OrchestrationMode.hybrid_retrieval:
            with start_span('eduassist.orchestration.public_retrieval', tracer_name='eduassist.ai_orchestrator.runtime'):
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
                query_hints = _extract_public_entity_hints(request.message)
                retrieval_supported = _retrieval_hits_cover_query_hints(retrieval_hits, query_hints)
                if retrieval_supported:
                    retrieval_hits = _filter_retrieval_hits_by_query_hints(retrieval_hits, query_hints)
                citations = _collect_citations(retrieval_hits)
                set_span_attributes(
                    **{
                        'eduassist.retrieval.hit_count': len(retrieval_hits),
                        'eduassist.retrieval.citation_count': len(citations),
                        'eduassist.retrieval.query_hint_count': len(query_hints),
                        'eduassist.retrieval.hints_supported': retrieval_supported,
                    }
                )
                if not retrieval_supported:
                    retrieval_hits = []
                    citations = []

                if preview.classification.domain is QueryDomain.calendar:
                    calendar_events = await _fetch_public_calendar(settings=settings)
                    set_span_attributes(**{'eduassist.calendar.event_count': len(calendar_events)})
        elif preview.mode is OrchestrationMode.graph_rag:
            with start_span('eduassist.orchestration.graph_rag', tracer_name='eduassist.ai_orchestrator.runtime'):
                set_span_attributes(
                    **{
                        'eduassist.graph_rag.workspace_ready': graph_rag_workspace_ready(settings.graph_rag_workspace),
                    }
                )
                graph_rag_answer = await run_graph_rag_query(
                    settings=settings,
                    query=request.message,
                )
                if graph_rag_answer is not None:
                    set_span_attributes(
                        **{
                            'eduassist.graph_rag.method': graph_rag_answer.get('method'),
                            'eduassist.graph_rag.response_length': len(graph_rag_answer.get('text', '')),
                        }
                    )
                else:
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
                        category=None,
                    )
                    retrieval_hits = search.hits
                    citations = _collect_citations(retrieval_hits)
                    set_span_attributes(
                        **{
                            'eduassist.graph_rag.fallback': True,
                            'eduassist.retrieval.hit_count': len(retrieval_hits),
                            'eduassist.retrieval.citation_count': len(citations),
                        }
                    )

        if preview.mode is OrchestrationMode.structured_tool:
            with start_span('eduassist.orchestration.structured_tool', tracer_name='eduassist.ai_orchestrator.runtime'):
                message_text = await _compose_structured_tool_answer(
                    settings=settings,
                    request=request,
                    preview=preview,
                    actor=actor,
                )
        elif preview.mode is OrchestrationMode.handoff:
            with start_span('eduassist.orchestration.handoff', tracer_name='eduassist.ai_orchestrator.runtime'):
                handoff_payload = await _create_support_handoff(
                    settings=settings,
                    request=request,
                    actor=actor,
                )
                if isinstance(handoff_payload, dict):
                    item = handoff_payload.get('item')
                    if isinstance(item, dict):
                        set_span_attributes(
                            **{
                                'eduassist.queue.name': item.get('queue_name'),
                                'eduassist.support.status': item.get('status'),
                                'eduassist.support.priority': item.get('priority_code'),
                                'eduassist.support.sla_state': item.get('sla_state'),
                            }
                        )
                message_text = _compose_handoff_answer(handoff_payload)
        elif preview.mode is OrchestrationMode.graph_rag and graph_rag_answer is not None:
            set_span_attributes(
                **{
                    'eduassist.orchestration.used_llm': False,
                    'eduassist.orchestration.graph_rag_live': True,
                }
            )
            message_text = graph_rag_answer['text']
        else:
            with start_span('eduassist.orchestration.answer_composition', tracer_name='eduassist.ai_orchestrator.runtime'):
                if preview.mode is OrchestrationMode.hybrid_retrieval and not retrieval_supported:
                    set_span_attributes(**{'eduassist.orchestration.used_llm': False})
                    message_text = _compose_public_gap_answer(query_hints)
                elif preview.mode is OrchestrationMode.hybrid_retrieval and _is_negative_requirement_query(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.answer_guardrail': 'negative_requirement_abstention',
                        }
                    )
                    message_text = _compose_negative_requirement_answer()
                elif preview.mode is OrchestrationMode.clarify and _is_prompt_disclosure_probe(request.message):
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': False,
                            'eduassist.orchestration.safe_clarify_guardrail': True,
                        }
                    )
                    message_text = (
                        f'{DEFAULT_PUBLIC_HELP} '
                        'Nao posso ajudar com detalhes internos de configuracao do sistema.'
                    )
                else:
                    llm_text = await compose_with_provider(
                        settings=settings,
                        request_message=request.message,
                        preview=preview,
                        citations=citations,
                        calendar_events=calendar_events,
                    )
                    set_span_attributes(
                        **{
                            'eduassist.orchestration.used_llm': bool(llm_text),
                            'eduassist.orchestration.llm_provider': settings.llm_provider,
                        }
                    )
                    message_text = llm_text or _compose_deterministic_answer(
                        preview=preview,
                        retrieval_hits=retrieval_hits,
                        citations=citations,
                        calendar_events=calendar_events,
                        query_hints=query_hints,
                    )

        if citations:
            sources = _render_source_lines(citations)
            if sources and sources not in message_text:
                message_text = f'{message_text}\n\n{sources}'

        set_span_attributes(**{'eduassist.response.length': len(message_text)})
        metric_attributes = {
            'mode': preview.mode.value,
            'domain': preview.classification.domain.value,
            'channel': request.channel.value,
            'authenticated': effective_user.authenticated,
            'retrieval_backend': preview.retrieval_backend.value,
        }
        record_counter(
            'eduassist_orchestration_responses',
            attributes=metric_attributes,
            description='Responses emitted by the AI orchestrator.',
        )
        record_histogram(
            'eduassist_orchestration_latency_ms',
            (monotonic() - started_at) * 1000,
            attributes=metric_attributes,
            description='End-to-end orchestration latency in milliseconds.',
        )
        record_histogram(
            'eduassist_orchestration_response_length',
            len(message_text),
            attributes=metric_attributes,
            description='Length of final responses emitted by the AI orchestrator.',
        )
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
