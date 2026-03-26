from __future__ import annotations

import asyncio
from collections import OrderedDict
import json
import re
from time import perf_counter
from typing import Any
import unicodedata

import httpx
from pydantic import BaseModel, Field

try:
    import crewai as crewai_pkg  # type: ignore
    from crewai import Agent, Crew, LLM, Process, Task  # type: ignore
except Exception:  # pragma: no cover
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = LLM = Process = Task = None  # type: ignore[assignment]


class ProtectedPilotPlan(BaseModel):
    intent: str = Field(min_length=1)
    student_name: str | None = None
    student_id: str | None = None
    domain: str = 'identity'
    attribute: str = 'general'
    needs_clarification: bool = False
    clarification_question: str | None = None
    relevant_sources: list[str] = Field(default_factory=list)


class ProtectedPilotAnswer(BaseModel):
    answer_text: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)


class ProtectedPilotJudge(BaseModel):
    valid: bool
    reason: str = ''
    revision_needed: bool = False


class EvidenceDoc(BaseModel):
    doc_id: str
    source: str
    title: str
    text: str


_PROTECTED_SHADOW_STATE: OrderedDict[str, dict[str, str]] = OrderedDict()
_PROTECTED_SHADOW_STATE_LIMIT = 256


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def _query_terms(message: str) -> set[str]:
    normalized = _normalize_text(message)
    return {
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in {'qual', 'quais', 'meus', 'minhas', 'meu', 'sua', 'seus', 'suas', 'por', 'para'}
    }


def _crewai_google_model(configured_model: str) -> str:
    base = str(configured_model or '').strip()
    if base.startswith('models/'):
        base = base.split('/', 1)[1]
    if base.startswith('gemini/'):
        base = base.split('/', 1)[1]
    if '-preview' in base:
        return 'gemini-2.5-flash'
    return base or 'gemini-2.5-flash'


def _build_llm(settings: Any) -> Any:
    if LLM is None:
        return None
    model_name = _crewai_google_model(
        str(getattr(settings, 'google_model', 'gemini-2.5-flash-preview') or 'gemini-2.5-flash-preview')
    )
    if not model_name.startswith('gemini/'):
        model_name = f'gemini/{model_name}'
    api_key = getattr(settings, 'google_api_key', None)
    if not api_key:
        return None
    return LLM(model=model_name, api_key=api_key, temperature=0.1, max_tokens=700)


async def _api_get(settings: Any, path: str) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    headers = {'X-Internal-Api-Token': getattr(settings, 'internal_api_token', 'dev-internal-token')}
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(f'{base_url}{path}', headers=headers)
    response.raise_for_status()
    body = response.json()
    return body if isinstance(body, dict) else {}


async def _load_actor_context(settings: Any, telegram_chat_id: int) -> dict[str, Any]:
    return await _api_get(settings, f'/v1/internal/identity/context?telegram_chat_id={telegram_chat_id}')


def _conversation_state_key(
    *,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
) -> str:
    if conversation_id:
        return f'{channel}:{conversation_id}'
    if telegram_chat_id is not None:
        return f'{channel}:telegram:{telegram_chat_id}'
    return f'{channel}:anonymous'


def _load_recent_student_name(state_key: str) -> str | None:
    state = _PROTECTED_SHADOW_STATE.get(state_key)
    if not isinstance(state, dict):
        return None
    value = str(state.get('student_name', '')).strip()
    return value or None


def _store_recent_student_name(state_key: str, student_name: str | None) -> None:
    if not student_name:
        return
    _PROTECTED_SHADOW_STATE[state_key] = {'student_name': str(student_name).strip()}
    _PROTECTED_SHADOW_STATE.move_to_end(state_key)
    while len(_PROTECTED_SHADOW_STATE) > _PROTECTED_SHADOW_STATE_LIMIT:
        _PROTECTED_SHADOW_STATE.popitem(last=False)


def _is_followup_style_message(message: str) -> bool:
    normalized = _normalize_text(message).strip()
    return (
        normalized.startswith('e ')
        or normalized.startswith('mas ')
        or any(term in normalized for term in {' dele', ' dela', ' desse aluno', ' dessa aluna', ' desse filho', ' dessa filha'})
    )


def _student_by_name(actor: dict[str, Any], student_name: str | None) -> dict[str, Any] | None:
    if not student_name:
        return None
    normalized_target = _normalize_text(student_name)
    for item in actor.get('linked_students') or []:
        if not isinstance(item, dict):
            continue
        if _normalize_text(str(item.get('full_name', ''))) == normalized_target:
            return item
    return None


def _is_student_focus_repair(message: str, student_name: str | None) -> bool:
    if not student_name:
        return False
    normalized = _normalize_text(message)
    first_name = _normalize_text(student_name).split()[0]
    if not first_name or first_name not in normalized:
        return False
    repair_markers = {
        'eu falei',
        'desse aluno',
        'desse filho',
        'desse estudante',
    }
    return any(marker in normalized for marker in repair_markers)


def _is_explicit_student_selection_message(message: str, student_name: str | None) -> bool:
    if not student_name:
        return False
    normalized = _normalize_text(message)
    normalized = re.sub(r'[^a-z0-9 ]+', ' ', normalized)
    normalized = ' '.join(normalized.split())
    if not normalized:
        return False
    full_name = _normalize_text(student_name).strip()
    first_name = full_name.split()[0] if full_name else ''
    reference_markers = {'meu filho', 'minha filha', 'o', 'a'}
    meaningful_tokens = [
        token
        for token in normalized.split()
        if token not in reference_markers
    ]
    info_request_terms = {
        'notas',
        'nota',
        'frequencia',
        'faltas',
        'provas',
        'prova',
        'avaliacoes',
        'documentacao',
        'documentos',
        'matricula',
        'financeiro',
        'boleto',
        'pagamento',
        'mensalidade',
    }
    if any(token in info_request_terms for token in meaningful_tokens):
        return False
    if not meaningful_tokens:
        return False
    if len(meaningful_tokens) > 4:
        return False
    if full_name and full_name in normalized:
        return True
    return bool(first_name and first_name in meaningful_tokens)


def _resolve_student(actor: dict[str, Any], message: str, *, recent_student_name: str | None = None) -> dict[str, Any] | None:
    linked_students = actor.get('linked_students') or []
    if not isinstance(linked_students, list):
        return None
    normalized_message = _normalize_text(message)
    matches: list[dict[str, Any]] = []
    for item in linked_students:
        if not isinstance(item, dict):
            continue
        full_name = _normalize_text(str(item.get('full_name', '')))
        first_name = full_name.split()[0] if full_name else ''
        if full_name and full_name in normalized_message:
            matches.append(item)
            continue
        if first_name and re.search(rf'\b{re.escape(first_name)}\b', normalized_message):
            matches.append(item)
    if len(matches) == 1:
        return matches[0]
    if recent_student_name and _is_followup_style_message(message):
        return _student_by_name(actor, recent_student_name)
    return None


def _extract_unmatched_student_reference(actor: dict[str, Any], message: str) -> str | None:
    linked_students = actor.get('linked_students') or []
    if not isinstance(linked_students, list) or not linked_students:
        return None
    normalized_message = _normalize_text(message)
    known_tokens: set[str] = set()
    for item in linked_students:
        if not isinstance(item, dict):
            continue
        full_name = _normalize_text(str(item.get('full_name', '')))
        for token in full_name.split():
            if len(token) >= 3:
                known_tokens.add(token)
    stopwords = {
        'quais', 'qual', 'do', 'da', 'de', 'meu', 'minha', 'filho', 'filha', 'as', 'os',
        'notas', 'nota', 'matricula', 'frequencia', 'faltas', 'provas', 'prova', 'documentacao',
        'documentos', 'situacao', 'status', 'como', 'estao', 'esta', 'está', 'estao', 'e',
    }
    for token in re.findall(r'[a-z0-9]+', normalized_message):
        if len(token) < 3 or token in stopwords:
            continue
        if token not in known_tokens:
            if any(marker in normalized_message for marker in {'filho', 'filha'}) or token.istitle():
                return token
    return None


def _requires_student(message: str) -> bool:
    terms = _query_terms(message)
    protected_terms = {
        'notas',
        'nota',
        'faltas',
        'frequencia',
        'provas',
        'prova',
        'financeiro',
        'boleto',
        'pagamento',
        'documentacao',
        'documentos',
        'matricula',
        'lucas',
        'ana',
    }
    return bool(terms & protected_terms)


def _is_identity_scope_query(message: str) -> bool:
    terms = _query_terms(message)
    identity_terms = {
        'filhos',
        'filho',
        'filha',
        'logado',
        'acesso',
        'dados',
        'vinculados',
        'vinculada',
        'conta',
    }
    return bool(terms & identity_terms)


async def _fetch_protected_evidence(
    *,
    settings: Any,
    actor_context: dict[str, Any],
    student: dict[str, Any] | None,
    telegram_chat_id: int,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {'identity': actor_context}
    if not student:
        return evidence
    student_id = student.get('student_id')
    if not student_id:
        return evidence

    endpoints = {
        'academic': f'/v1/students/{student_id}/academic-summary?telegram_chat_id={telegram_chat_id}',
        'admin': f'/v1/students/{student_id}/administrative-status?telegram_chat_id={telegram_chat_id}',
        'financial': f'/v1/students/{student_id}/financial-summary?telegram_chat_id={telegram_chat_id}',
        'assessments': f'/v1/students/{student_id}/upcoming-assessments?telegram_chat_id={telegram_chat_id}',
        'attendance': f'/v1/students/{student_id}/attendance-timeline?telegram_chat_id={telegram_chat_id}',
    }
    results = await asyncio.gather(*(_api_get(settings, path) for path in endpoints.values()))
    for key, payload in zip(endpoints.keys(), results, strict=True):
        evidence[key] = payload
    return evidence


def _build_protected_docs(evidence: dict[str, Any]) -> list[EvidenceDoc]:
    docs: list[EvidenceDoc] = []

    def add(doc_id: str, source: str, title: str, text: str) -> None:
        cleaned = ' '.join(str(text or '').split()).strip()
        if cleaned:
            docs.append(EvidenceDoc(doc_id=doc_id, source=source, title=title, text=cleaned))

    identity_actor = evidence.get('identity', {}).get('actor', {})
    if isinstance(identity_actor, dict):
        add(
            'identity.actor',
            'identity',
            'Identidade do responsavel',
            (
                f"Responsavel autenticado: {identity_actor.get('full_name', '')}. "
                f"Papel: {identity_actor.get('role_code', '')}. "
                f"Alunos vinculados: {'; '.join(str(item.get('full_name', '')) for item in identity_actor.get('linked_students', []) if isinstance(item, dict))}."
            ),
        )
        for index, item in enumerate(identity_actor.get('linked_students', []), start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'identity.student.{index}',
                'identity',
                str(item.get('full_name', f'Aluno {index}')),
                (
                    f"matricula {item.get('enrollment_code', '')} | turma {item.get('class_name', '')} | "
                    f"academico={item.get('can_view_academic')} | financeiro={item.get('can_view_finance')}"
                ),
            )

    academic = evidence.get('academic', {}).get('summary', {})
    if isinstance(academic, dict):
        attendance_summary = academic.get('attendance')
        attendance_records = attendance_summary if isinstance(attendance_summary, list) else []
        attendance_overview = ''
        if isinstance(attendance_summary, dict):
            attendance_overview = str(attendance_summary.get('presence_rate', '') or '')
        elif attendance_records:
            absent = sum(1 for item in attendance_records if isinstance(item, dict) and item.get('status') == 'absent')
            late = sum(1 for item in attendance_records if isinstance(item, dict) and item.get('status') == 'late')
            attendance_overview = f'{len(attendance_records)} registro(s), {absent} falta(s), {late} atraso(s)'
        add(
            'academic.overview',
            'academic',
            f"Resumo academico de {academic.get('student_name', 'aluno')}",
            (
                f"Aluno: {academic.get('student_name', '')}. Turma: {academic.get('class_name', '')}. "
                f"Matricula: {academic.get('enrollment_code', '')}. "
                f"Quantidade de notas: {len(academic.get('grades', []) or [])}. "
                f"Resumo de frequencia: {attendance_overview or 'nao informado'}."
            ),
        )
        for index, item in enumerate((academic.get('grades') or [])[:12], start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'academic.grade.{index}',
                'academic',
                f"{item.get('subject_name', 'Disciplina')} - {item.get('item_title', 'avaliacao')}",
                f"Termo {item.get('term_code', '')} | nota {item.get('score', '')}/{item.get('max_score', '')} | feedback {item.get('feedback', '')}",
            )

    admin = evidence.get('admin', {}).get('summary', {})
    if isinstance(admin, dict):
        add(
            'admin.overview',
            'admin',
            f"Status administrativo de {admin.get('student_name', 'aluno')}",
            (
                f"Situacao geral: {admin.get('overall_status', '')}. "
                f"Proximo passo: {admin.get('next_step') or 'nenhum'}. "
                f"Matricula: {admin.get('enrollment_code', '')}."
            ),
        )
        for index, item in enumerate(admin.get('checklist', []) or [], start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'admin.check.{index}',
                'admin',
                str(item.get('label', f'Checklist {index}')),
                f"Status {item.get('status', '')} | notas {item.get('notes', '')}",
            )

    financial = evidence.get('financial', {}).get('summary', {})
    if isinstance(financial, dict):
        add(
            'financial.overview',
            'financial',
            f"Resumo financeiro de {financial.get('student_name', 'aluno')}",
            (
                f"Mensalidade {financial.get('monthly_amount', '')}. "
                f"Contrato {financial.get('contract_code', '')}. "
                f"Faturas em aberto {financial.get('open_invoice_count', '')}. "
                f"Faturas vencidas {financial.get('overdue_invoice_count', '')}."
            ),
        )
        for index, item in enumerate(financial.get('invoices', []) or [], start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'financial.invoice.{index}',
                'financial',
                f"Fatura {item.get('reference_month', '')}",
                (
                    f"Vencimento {item.get('due_date', '')} | valor {item.get('amount_due', '')} | "
                    f"status {item.get('status', '')} | pago {item.get('paid_amount', '')}"
                ),
            )

    assessments = evidence.get('assessments', {}).get('summary', {})
    if isinstance(assessments, dict):
        add(
            'assessments.overview',
            'assessments',
            f"Proximas avaliacoes de {assessments.get('student_name', 'aluno')}",
            f"Quantidade de avaliacoes: {len(assessments.get('assessments', []) or [])}.",
        )
        for index, item in enumerate((assessments.get('assessments') or [])[:12], start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'assessments.item.{index}',
                'assessments',
                f"{item.get('subject_name', 'Disciplina')} - {item.get('item_title', 'avaliacao')}",
                f"Termo {item.get('term_code', '')} | data {item.get('due_date', '')}",
            )

    attendance = evidence.get('attendance', {}).get('summary', {})
    if isinstance(attendance, dict):
        add(
            'attendance.overview',
            'attendance',
            f"Frequencia de {attendance.get('student_name', 'aluno')}",
            f"Quantidade de registros: {len(attendance.get('records', []) or [])}.",
        )
        for index, item in enumerate((attendance.get('records') or [])[:12], start=1):
            if not isinstance(item, dict):
                continue
            add(
                f'attendance.record.{index}',
                'attendance',
                f"{item.get('subject_name', 'Disciplina')} em {item.get('record_date', '')}",
                f"Status {item.get('status', '')} | minutos ausente {item.get('minutes_absent', '')}",
            )
    return docs


def _rank_docs(message: str, docs: list[EvidenceDoc], *, limit: int = 8) -> list[EvidenceDoc]:
    terms = _query_terms(message)
    ranked: list[tuple[int, int, EvidenceDoc]] = []
    for doc in docs:
        haystack = _normalize_text(f'{doc.title} {doc.text}')
        score = sum(5 if term in _normalize_text(doc.title) else 2 for term in terms if term in haystack)
        if any(term in terms for term in {'notas', 'nota'}) and doc.doc_id.startswith('academic.'):
            score += 6
        if any(term in terms for term in {'faltas', 'frequencia'}) and doc.doc_id.startswith('attendance.'):
            score += 6
        if any(term in terms for term in {'provas', 'prova', 'avaliacoes'}) and doc.doc_id.startswith('assessments.'):
            score += 6
        if any(term in terms for term in {'financeiro', 'boleto', 'pagamento', 'mensalidade'}) and doc.doc_id.startswith('financial.'):
            score += 6
        if any(term in terms for term in {'documentacao', 'documentos'}) and doc.doc_id.startswith('admin.'):
            score += 6
        if any(term in terms for term in {'filhos', 'filho', 'filha', 'logado', 'acesso'}) and doc.doc_id.startswith('identity.'):
            score += 6
        ranked.append((score, len(doc.text), doc))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen = [doc for score, _, doc in ranked if score > 0][:limit]
    return chosen or docs[:limit]


def _serialize_docs(docs: list[EvidenceDoc]) -> str:
    return '\n\n'.join(f'[{doc.doc_id}] {doc.title}\nFonte: {doc.source}\nConteudo: {doc.text}' for doc in docs)


def _identity_backstop(actor: dict[str, Any], message: str) -> str | None:
    terms = _query_terms(message)
    linked = [item for item in actor.get('linked_students', []) if isinstance(item, dict)]
    record_terms = {
        'notas',
        'nota',
        'frequencia',
        'faltas',
        'provas',
        'prova',
        'avaliacoes',
        'documentacao',
        'documentos',
        'matricula',
        'financeiro',
        'boleto',
        'pagamento',
        'mensalidade',
    }
    if any(term in terms for term in {'logado', 'acesso'}):
        names = ', '.join(str(item.get('full_name', '')) for item in linked)
        return (
            f"Voce esta autenticado aqui como {actor.get('full_name', 'responsavel')}. "
            f"Sua conta esta vinculada a {names} e pode consultar notas, frequencia, avaliacoes, documentacao e financeiro desses alunos."
        )
    if any(term in terms for term in {'filhos', 'filho', 'filha'}) and not (terms & record_terms):
        names = ', '.join(str(item.get('full_name', '')) for item in linked)
        return f"Sua conta esta vinculada a {names}."
    return None


def _auth_required_backstop() -> str:
    return (
        'Essa consulta depende de autenticacao e vinculo da sua conta no Telegram. '
        'Use o portal da escola para gerar o codigo de vinculacao e depois envie o comando /start link_<codigo> ao bot.'
    )


def _humanize_admin_status(raw_status: Any) -> str:
    normalized = _normalize_text(str(raw_status or ''))
    mapping = {
        'complete': 'regular e completa',
        'completed': 'regular e completa',
        'pending': 'com pendencias',
        'incomplete': 'incompleta',
        'missing': 'com pendencias',
    }
    return mapping.get(normalized, str(raw_status or 'regular'))


def _student_backstop(message: str, student: dict[str, Any] | None, evidence: dict[str, Any], docs: list[EvidenceDoc]) -> str | None:
    if not student:
        return None
    terms = _query_terms(message)
    name = str(student.get('full_name', 'o aluno'))
    if any(term in terms for term in {'notas', 'nota'}):
        grades = (evidence.get('academic', {}).get('summary', {}) or {}).get('grades', []) or []
        top = [item for item in grades[:3] if isinstance(item, dict)]
        if top:
            parts = [f"{item.get('subject_name')}: {item.get('score')}/{item.get('max_score')}" for item in top]
            return f"As notas mais recentes de {name} incluem " + '; '.join(parts) + '.'
    if any(term in terms for term in {'faltas', 'frequencia'}):
        records = (evidence.get('attendance', {}).get('summary', {}) or {}).get('records', []) or []
        absent = sum(1 for item in records if isinstance(item, dict) and item.get('status') == 'absent')
        late = sum(1 for item in records if isinstance(item, dict) and item.get('status') == 'late')
        if 'frequencia' in terms and 'faltas' not in terms:
            total = len(records)
            present = sum(1 for item in records if isinstance(item, dict) and item.get('status') == 'present')
            return (
                f'Na frequencia de {name}, eu encontrei {total} registro(s) neste recorte: '
                f'{present} presenca(s), {absent} falta(s) e {late} atraso(s).'
            )
        return f"{name} tem {absent} falta(s) e {late} registro(s) de atraso neste recorte."
    if any(term in terms for term in {'provas', 'prova', 'avaliacoes'}):
        assessments = (evidence.get('assessments', {}).get('summary', {}) or {}).get('assessments', []) or []
        first = next((item for item in assessments if isinstance(item, dict)), None)
        if first:
            return f"A proxima avaliacao registrada de {name} e {first.get('item_title')} em {first.get('due_date')}."
    if any(term in terms for term in {'financeiro', 'pagamento', 'mensalidade', 'boleto'}):
        summary = (evidence.get('financial', {}).get('summary', {}) or {})
        invoices = [item for item in (summary.get('invoices') or []) if isinstance(item, dict)]
        open_invoices = [item for item in invoices if str(item.get('status', '')).lower() == 'open']
        if 'proximo' in terms:
            next_invoice = sorted(open_invoices or invoices, key=lambda item: str(item.get('due_date', '')))[0] if (open_invoices or invoices) else None
            if next_invoice and str(next_invoice.get('status', '')).lower() == 'open':
                return (
                    f"O proximo pagamento de {name} vence em {next_invoice.get('due_date')} "
                    f"no valor de {next_invoice.get('amount_due')}."
                )
            return f"No momento, nao vejo fatura em aberto para {name} neste recorte."
        return (
            f"No financeiro de {name}, a mensalidade de referencia e {summary.get('monthly_amount')} "
            f"e ha {summary.get('open_invoice_count')} fatura(s) em aberto, sendo {summary.get('overdue_invoice_count')} vencida(s)."
        )
    if any(term in terms for term in {'documentacao', 'documentos'}):
        summary = (evidence.get('admin', {}).get('summary', {}) or {})
        return f"A situacao documental de {name} hoje esta {_humanize_admin_status(summary.get('overall_status'))}."
    if 'matricula' in terms:
        summary = (evidence.get('admin', {}).get('summary', {}) or {})
        return f"A matricula de {name} e {summary.get('enrollment_code')}."
    return None


def _student_focus_backstop(message: str, student: dict[str, Any] | None) -> str | None:
    if not isinstance(student, dict):
        return None
    name = str(student.get('full_name', '')).strip()
    if not name:
        return None
    if _is_explicit_student_selection_message(message, name):
        return (
            f'Perfeito, seguimos com {name}. '
            'Posso te ajudar com notas, frequencia, faltas, proximas provas, documentacao, matricula e financeiro.'
        )
    if _is_student_focus_repair(message, name):
        return (
            f'Perfeito, seguimos com {name}. '
            'Posso te ajudar com notas, faltas, proximas provas, documentacao, matricula e financeiro.'
        )
    return None


async def run_protected_crewai_pilot(
    *,
    message: str,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
    settings: Any,
) -> dict[str, Any]:
    normalized_message = ' '.join(message.strip().lower().split())
    overall_started_at = perf_counter()
    if Crew is None or Agent is None or Task is None or Process is None:
        return {'engine_name': 'crewai', 'executed': False, 'reason': 'crewai_dependency_unavailable', 'metadata': {'slice_name': 'protected'}}
    if telegram_chat_id is None:
        return {'engine_name': 'crewai', 'executed': False, 'reason': 'protected_shadow_requires_telegram_chat_id', 'metadata': {'slice_name': 'protected'}}

    actor_context = await _load_actor_context(settings, telegram_chat_id)
    actor = actor_context.get('actor') or {}
    if not isinstance(actor, dict) or not actor.get('authenticated'):
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_actor_not_authenticated',
            'metadata': {
                'slice_name': 'protected',
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'normalized_message': normalized_message,
                'answer': {'answer_text': _auth_required_backstop()},
                'judge': {'valid': True, 'reason': 'auth_required_guidance', 'revision_needed': False},
                'deterministic_backstop_used': True,
            },
        }
    state_key = _conversation_state_key(
        conversation_id=conversation_id,
        telegram_chat_id=telegram_chat_id,
        channel=channel,
    )
    recent_student_name = _load_recent_student_name(state_key)

    identity_backstop = _identity_backstop(actor, message)
    if identity_backstop and _is_identity_scope_query(message):
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_identity_backstop',
            'metadata': {
                'slice_name': 'protected',
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'normalized_message': normalized_message,
                'answer': {'answer_text': identity_backstop},
                'judge': {'valid': True, 'reason': 'identity_scope_handled_deterministically', 'revision_needed': False},
                'deterministic_backstop_used': True,
            },
        }

    student = _resolve_student(actor, message, recent_student_name=recent_student_name)
    student_focus_answer = _student_focus_backstop(message, student)
    if student_focus_answer:
        _store_recent_student_name(state_key, student.get('full_name') if isinstance(student, dict) else None)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_student_focus_backstop',
            'metadata': {
                'slice_name': 'protected',
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'normalized_message': normalized_message,
                'answer': {'answer_text': student_focus_answer},
                'judge': {'valid': True, 'reason': 'student_focus_repair_handled_deterministically', 'revision_needed': False},
                'resolved_student_name': student.get('full_name') if isinstance(student, dict) else None,
                'deterministic_backstop_used': True,
            },
        }
    unmatched_student_reference = _extract_unmatched_student_reference(actor, message)
    if unmatched_student_reference:
        names = ', '.join(str(item.get('full_name', '')) for item in actor.get('linked_students', []) if isinstance(item, dict))
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_unmatched_student_reference',
            'metadata': {
                'slice_name': 'protected',
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'normalized_message': normalized_message,
                'answer': {
                    'answer_text': (
                        f'Hoje eu nao encontrei {unmatched_student_reference.title()} entre os alunos vinculados a esta conta. '
                        f'No momento, os alunos que aparecem aqui sao: {names}. '
                        'Se quiser, me diga qual deles voce quer consultar.'
                    )
                },
                'judge': {'valid': True, 'reason': 'unmatched_student_handled_deterministically', 'revision_needed': False},
                'deterministic_backstop_used': True,
            },
        }
    if _requires_student(message) and student is None and len(actor.get('linked_students', []) or []) > 1:
        names = ', '.join(str(item.get('full_name', '')) for item in actor.get('linked_students', []) if isinstance(item, dict))
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'protected_shadow_needs_student_clarification',
            'metadata': {
                'slice_name': 'protected',
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'normalized_message': normalized_message,
                'answer': {'answer_text': f'Posso te ajudar com {names}. Me diga qual aluno voce quer consultar.'},
                'judge': {'valid': True, 'reason': 'student_clarification_required', 'revision_needed': False},
                'deterministic_backstop_used': True,
            },
        }

    evidence = await _fetch_protected_evidence(
        settings=settings,
        actor_context=actor_context,
        student=student,
        telegram_chat_id=telegram_chat_id,
    )
    docs = _build_protected_docs(evidence)
    shortlisted_docs = _rank_docs(message, docs)
    fast_path_answer = identity_backstop or _student_backstop(message, student, evidence, shortlisted_docs)
    if isinstance(fast_path_answer, str) and fast_path_answer.strip():
        _store_recent_student_name(state_key, student.get('full_name') if isinstance(student, dict) else None)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_protected_fast_path',
            'metadata': {
                'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
                'slice_name': 'protected',
                'normalized_message': normalized_message,
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': [],
                'task_names': [],
                'latency_ms': round((perf_counter() - overall_started_at) * 1000, 1),
                'plan': None,
                'answer': {'answer_text': fast_path_answer, 'citations': [shortlisted_docs[0].doc_id] if shortlisted_docs else []},
                'judge': {'valid': True, 'reason': 'deterministic_fast_path', 'revision_needed': False},
                'evidence_sources': [doc.doc_id for doc in shortlisted_docs],
                'resolved_student_name': student.get('full_name') if isinstance(student, dict) else None,
                'deterministic_backstop_used': True,
            },
        }

    llm = _build_llm(settings)
    if llm is None:
        return {'engine_name': 'crewai', 'executed': False, 'reason': 'crewai_llm_not_configured', 'metadata': {'slice_name': 'protected'}}
    evidence_bundle = _serialize_docs(shortlisted_docs)

    planner = Agent(
        role='Protected question planner',
        goal='Resolve the protected intent, student scope, and attribute using only the shortlisted protected docs.',
        backstory='You plan protected school-support answers carefully and must not leak data between students.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    composer = Agent(
        role='Protected grounded composer',
        goal='Compose a short, human, precise answer in pt-BR using only the shortlisted protected docs.',
        backstory='You never mix students, invent values, or answer outside the linked account scope.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    judge = Agent(
        role='Protected answer judge',
        goal='Reject answers that switch student, actor, amount, enrollment, dates, or statuses beyond the protected docs.',
        backstory='You are strict about entity safety and scope.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )

    planning_task = Task(
        name='protected_planning',
        description=(
            'Pergunta do usuario: {message}\n'
            'Docs protegidos mais relevantes:\n{evidence_bundle}\n\n'
            'Retorne um plano estruturado com intencao, aluno, dominio, atributo, se precisa de esclarecimento e ids das fontes relevantes.'
        ),
        expected_output='Structured protected plan.',
        agent=planner,
        output_pydantic=ProtectedPilotPlan,
    )
    composition_task = Task(
        name='protected_composition',
        description=(
            'Com base na pergunta do usuario, no plano e nos docs protegidos, responda em pt-BR de forma curta e humana.\n'
            'Nunca misture alunos. Nunca invente notas, faltas, valores, codigos ou datas.'
        ),
        expected_output='Structured protected answer.',
        agent=composer,
        context=[planning_task],
        output_pydantic=ProtectedPilotAnswer,
    )
    judge_task = Task(
        name='protected_judging',
        description=(
            'Revise o plano e a resposta final. Marque como invalida qualquer resposta que troque aluno, ator, codigo, valor, data ou status.'
        ),
        expected_output='Structured protected judge result.',
        agent=judge,
        context=[planning_task, composition_task],
        output_pydantic=ProtectedPilotJudge,
    )

    crew = Crew(
        name='eduassist_protected_shadow',
        agents=[planner, composer, judge],
        tasks=[planning_task, composition_task, judge_task],
        process=Process.sequential,
        verbose=False,
        cache=False,
        memory=False,
        tracing=False,
    )

    await asyncio.to_thread(crew.kickoff, inputs={'message': message, 'evidence_bundle': evidence_bundle})
    latency_ms = round((perf_counter() - overall_started_at) * 1000, 1)

    plan = getattr(planning_task.output, 'pydantic', None)
    answer = getattr(composition_task.output, 'pydantic', None)
    verdict = getattr(judge_task.output, 'pydantic', None)

    backstop_answer = identity_backstop or _student_backstop(message, student, evidence, shortlisted_docs)
    backstop_used = False
    if isinstance(backstop_answer, str) and backstop_answer.strip():
        answer = ProtectedPilotAnswer(answer_text=backstop_answer, citations=[shortlisted_docs[0].doc_id] if shortlisted_docs else [])
        verdict = ProtectedPilotJudge(valid=True, reason='deterministic_backstop_applied', revision_needed=False)
        backstop_used = True

    metadata = {
        'conversation_id': conversation_id or f'telegram:{telegram_chat_id}',
        'slice_name': 'protected',
        'normalized_message': normalized_message,
        'crewai_installed': True,
        'crewai_version': getattr(crewai_pkg, '__version__', None),
        'agent_roles': ['planner', 'composer', 'judge'],
        'task_names': ['protected_planning', 'protected_composition', 'protected_judging'],
        'latency_ms': latency_ms,
        'plan': plan.model_dump(mode='json') if isinstance(plan, ProtectedPilotPlan) else None,
        'answer': answer.model_dump(mode='json') if isinstance(answer, ProtectedPilotAnswer) else None,
        'judge': verdict.model_dump(mode='json') if isinstance(verdict, ProtectedPilotJudge) else None,
        'evidence_sources': [doc.doc_id for doc in shortlisted_docs],
        'resolved_student_name': student.get('full_name') if isinstance(student, dict) else None,
        'deterministic_backstop_used': backstop_used,
    }
    _store_recent_student_name(state_key, student.get('full_name') if isinstance(student, dict) else None)
    return {
        'engine_name': 'crewai',
        'executed': True,
        'reason': 'crewai_protected_pilot_completed',
        'metadata': metadata,
    }
