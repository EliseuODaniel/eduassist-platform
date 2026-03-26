from __future__ import annotations

import asyncio
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
except Exception:  # pragma: no cover - defensive import
    crewai_pkg = None  # type: ignore[assignment]
    Agent = Crew = LLM = Process = Task = None  # type: ignore[assignment]


class PublicPilotPlan(BaseModel):
    intent: str = Field(min_length=1)
    entity: str = Field(default='school')
    attribute: str = Field(default='general')
    needs_clarification: bool = False
    clarification_question: str | None = None
    relevant_sources: list[str] = Field(default_factory=list)


class PublicPilotAnswer(BaseModel):
    answer_text: str = Field(min_length=1)
    citations: list[str] = Field(default_factory=list)


class PublicPilotJudge(BaseModel):
    valid: bool
    reason: str = ''
    revision_needed: bool = False


class EvidenceDoc(BaseModel):
    doc_id: str
    source: str
    title: str
    text: str


def _crewai_google_model(configured_model: str) -> str:
    base = str(configured_model or '').strip()
    if base.startswith('models/'):
        base = base.split('/', 1)[1]
    if base.startswith('gemini/'):
        base = base.split('/', 1)[1]
    if '-preview' in base:
        return 'gemini-2.5-flash'
    return base or 'gemini-2.5-flash'


async def _fetch_public_evidence(settings: Any) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    async with httpx.AsyncClient(timeout=15.0) as client:
        responses = await asyncio.gather(
            client.get(f'{base_url}/v1/public/school-profile'),
            client.get(f'{base_url}/v1/public/org-directory'),
            client.get(f'{base_url}/v1/public/timeline'),
            client.get(f'{base_url}/v1/calendar/public'),
        )
    payloads: dict[str, Any] = {}
    names = ('school_profile', 'org_directory', 'timeline', 'calendar_events')
    for name, response in zip(names, responses, strict=True):
        response.raise_for_status()
        payloads[name] = response.json()
    return payloads


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()


def _query_terms(message: str) -> set[str]:
    normalized = _normalize_text(message)
    return {
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in {'qual', 'quais', 'essa', 'esse', 'esta', 'sobre', 'colegio', 'escola', 'porque'}
    }


def _stringify_items(items: list[Any], keys: tuple[str, ...]) -> list[str]:
    lines: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        parts = [str(item.get(key, '')).strip() for key in keys if str(item.get(key, '')).strip()]
        if parts:
            lines.append(' | '.join(parts))
    return lines


def _build_evidence_docs(evidence: dict[str, Any]) -> list[EvidenceDoc]:
    profile = evidence.get('school_profile', {}).get('profile', {})
    directory = evidence.get('org_directory', {}).get('directory', {})
    timeline_entries = evidence.get('timeline', {}).get('timeline', {}).get('entries', [])
    calendar_events = evidence.get('calendar_events', {}).get('events', [])

    docs: list[EvidenceDoc] = []

    def add(doc_id: str, source: str, title: str, text: str) -> None:
        cleaned = ' '.join(str(text or '').split()).strip()
        if cleaned:
            docs.append(EvidenceDoc(doc_id=doc_id, source=source, title=title, text=cleaned))

    add(
        'profile.overview',
        'school_profile',
        'Visao geral institucional',
        (
            f"{profile.get('school_name', 'Colegio Horizonte')} em {profile.get('city', 'Sao Paulo')}/{profile.get('state', 'SP')}. "
            f"{profile.get('short_headline', '')} {profile.get('education_model', '')}"
        ),
    )
    add(
        'profile.location',
        'school_profile',
        'Endereco e presenca digital',
        (
            f"Endereco: {profile.get('address_line', '')}, {profile.get('district', '')}, {profile.get('city', '')}/{profile.get('state', '')}, CEP {profile.get('postal_code', '')}. "
            f"Site: {profile.get('website_url', '')}. Fax: {profile.get('fax_number') or 'nao utiliza fax institucional'}."
        ),
    )
    add(
        'profile.segments',
        'school_profile',
        'Segmentos, turnos e curriculo',
        (
            f"Segmentos: {'; '.join(str(item) for item in profile.get('segments', []))}. "
            f"Base curricular: {profile.get('curriculum_basis', '')}. "
            f"Turnos: {'; '.join(_stringify_items(profile.get('shift_offers', []), ('segment', 'shift_label', 'starts_at', 'ends_at', 'notes')))}."
        ),
    )
    add('profile.contacts', 'school_profile', 'Canais oficiais', '; '.join(_stringify_items(profile.get('contact_channels', []), ('channel', 'label', 'value'))))
    add('profile.features', 'school_profile', 'Espacos, atividades e diferenciais', '; '.join(_stringify_items(profile.get('feature_inventory', []), ('name', 'category', 'summary', 'hours'))))
    add('profile.tuition', 'school_profile', 'Valores publicos e politica comercial', '; '.join(_stringify_items(profile.get('tuition_reference', []), ('segment', 'shift_label', 'monthly_amount', 'enrollment_fee', 'notes'))))
    add('profile.visits', 'school_profile', 'Visitas e admissoes', '; '.join(_stringify_items(profile.get('visit_offers', []), ('title', 'schedule_hint', 'notes'))))
    add(
        'profile.documents',
        'school_profile',
        'Envio de documentos',
        json.dumps(profile.get('document_submission_policy', {}), ensure_ascii=False),
    )
    add(
        'profile.required_documents',
        'school_profile',
        'Documentos exigidos para matricula',
        '; '.join(str(item).strip() for item in (profile.get('admissions_required_documents') or []) if str(item).strip()),
    )
    add(
        'directory.leadership',
        'org_directory',
        'Lideranca e contatos',
        '; '.join(_stringify_items(directory.get('leadership_team', []), ('name', 'title', 'focus', 'contact_channel', 'notes'))),
    )
    add(
        'directory.channels',
        'org_directory',
        'Diretorio de canais',
        '; '.join(_stringify_items(directory.get('contact_channels', []), ('channel', 'label', 'value'))),
    )

    for index, item in enumerate(profile.get('feature_inventory', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'feature.{index}',
            'school_profile',
            str(item.get('label', item.get('feature_key', f'Espaco {index}'))),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('feature_key', 'category', 'available', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('contact_channels', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'contact.{index}',
            'school_profile',
            f"{item.get('label', 'Contato')} ({item.get('channel', 'canal')})",
            ' | '.join(str(item.get(key, '')).strip() for key in ('value',) if str(item.get(key, '')).strip()),
        )

    for index, item in enumerate(profile.get('tuition_reference', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'tuition.{index}',
            'school_profile',
            str(item.get('segment', f'Faixa {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('shift_label', 'monthly_amount', 'enrollment_fee', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('visit_offers', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'visit.{index}',
            'school_profile',
            str(item.get('title', f'Visita {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('schedule_hint', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('admissions_highlights', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'admissions.{index}',
            'school_profile',
            str(item.get('title', f'Admissoes {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('summary',)
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('highlights', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'highlight.{index}',
            'school_profile',
            str(item.get('title', f'Diferencial {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('summary',)
                if str(item.get(key, '')).strip()
            ),
        )

    for index, entry in enumerate(timeline_entries, start=1):
        if not isinstance(entry, dict):
            continue
        add(
            f'timeline.{index}',
            'timeline',
            str(entry.get('title', f'Evento institucional {index}')),
            ' | '.join(
                str(entry.get(key, '')).strip()
                for key in ('summary', 'event_date', 'audience', 'notes')
                if str(entry.get(key, '')).strip()
            ),
        )

    for index, event in enumerate(calendar_events, start=1):
        if not isinstance(event, dict):
            continue
        add(
            f'calendar.{index}',
            'calendar_events',
            str(event.get('title', f'Evento publico {index}')),
            ' | '.join(
                str(event.get(key, '')).strip()
                for key in ('description', 'category', 'starts_at', 'ends_at')
                if str(event.get(key, '')).strip()
            ),
        )

    return docs


def _rank_evidence_docs(message: str, docs: list[EvidenceDoc], *, limit: int = 6) -> list[EvidenceDoc]:
    terms = _query_terms(message)
    if not terms:
        return docs[:limit]

    ranked: list[tuple[int, int, EvidenceDoc]] = []
    for doc in docs:
        haystack = _normalize_text(f'{doc.title} {doc.text}')
        score = sum(5 if term in _normalize_text(doc.title) else 2 for term in terms if term in haystack)
        if any(term in haystack for term in ('biblioteca', 'biblioteca aurora')) and any(
            term in terms for term in ('biblioteca', 'horario', 'hora')
        ):
            score += 4
        if any(term in haystack for term in ('matricula', 'admissoes')) and any(
            term in terms for term in ('matricula', 'admissao', 'inscricao')
        ):
            score += 4
        if any(term in haystack for term in ('fax', 'instagram', 'telefone', 'whatsapp', 'email')) and any(
            term in terms for term in ('fax', 'instagram', 'telefone', 'whatsapp', 'email', 'contato', 'ligo', 'ligar')
        ):
            score += 4
        ranked.append((score, len(doc.text), doc))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    shortlisted = [doc for score, _, doc in ranked if score > 0][:limit]
    return shortlisted or docs[:limit]


def _serialize_evidence_pack(docs: list[EvidenceDoc]) -> str:
    return '\n\n'.join(
        f"[{doc.doc_id}] {doc.title}\nFonte: {doc.source}\nConteudo: {doc.text}"
        for doc in docs
    )


def _select_primary_doc(plan: PublicPilotPlan | None, docs: list[EvidenceDoc]) -> EvidenceDoc | None:
    if isinstance(plan, PublicPilotPlan):
        selected = [doc for doc in docs if doc.doc_id in set(plan.relevant_sources)]
        if selected:
            return selected[0]
    return docs[0] if docs else None


def _find_first_matching_doc(docs: list[EvidenceDoc], prefix: str, terms: tuple[str, ...]) -> EvidenceDoc | None:
    for doc in docs:
        if not doc.doc_id.startswith(prefix):
            continue
        haystack = _normalize_text(f'{doc.title} {doc.text}')
        if any(term in haystack for term in terms):
            return doc
    return None


def _direct_contact_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    if not ({'telefone', 'fax', 'ligo', 'ligar', 'contato', 'caixa', 'postal', 'telegrama'} & terms):
        return None
    phone_doc = _find_first_matching_doc(docs, 'contact.', ('telefone', 'phone', 'secretaria'))
    fax_doc = _find_first_matching_doc(docs, 'profile.', ('fax',))
    phone_answer = None
    fax_answer = None
    if phone_doc is not None:
        phone_answer = f"{phone_doc.title}: {phone_doc.text.replace('|', ' ').strip()}"
    if fax_doc is not None and 'nao utiliza fax' in _normalize_text(fax_doc.text):
        fax_answer = 'Hoje a escola nao utiliza fax institucional.'
    fallback_channels = 'portal institucional, email da secretaria ou secretaria presencial'
    normalized_message = _normalize_text(message)
    if 'fax' in terms and any(term in normalized_message for term in ('antes voce respondeu', 'antes você respondeu', 'corrigindo', 'mas antes')):
        return (
            'Voce esta certo em cobrar essa correcao. '
            'Corrigindo: hoje a escola nao utiliza fax institucional. '
            f'Para documentos, use {fallback_channels}.'
        )
    if 'fax' in terms and any(term in normalized_message for term in ('enviar', 'envio', 'documento', 'documentos')):
        return (
            'Hoje a escola nao utiliza fax para envio de documentos. '
            f'Para isso, use {fallback_channels}.'
        )
    if 'telegrama' in terms:
        return f'Hoje a escola nao publica telegrama como canal valido. Para documentos, use {fallback_channels}.'
    if {'caixa', 'postal'} & terms:
        return f'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. Para documentos, use {fallback_channels}.'
    if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and 'fax' in terms and phone_answer and fax_answer:
        return f'{phone_answer} {fax_answer}'
    if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and phone_answer:
        return phone_answer
    if 'fax' in terms and fax_answer:
        return 'Hoje nao existe numero de fax publicado, porque a escola nao utiliza fax institucional.'
    return None


def _direct_feature_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    feature_prompt_terms = {'atividades', 'atividade', 'complementares', 'complementar', 'oficinas', 'esporte', 'esportes', 'maker'}
    if not (feature_prompt_terms & terms):
        return None
    feature_docs = [doc for doc in docs if doc.doc_id.startswith('feature.')]
    if not feature_docs:
        return None
    selected_labels: list[str] = []
    selected_texts: list[str] = []
    for doc in feature_docs:
        normalized = _normalize_text(f'{doc.title} {doc.text}')
        if any(term in normalized for term in ('maker', 'futsal', 'volei', 'biblioteca', 'laboratorio')):
            selected_labels.append(doc.title)
            selected_texts.append(doc.text)
    if not selected_labels:
        selected_labels = [doc.title for doc in feature_docs[:4]]
    labels_preview = ', '.join(selected_labels[:4])
    detail_parts: list[str] = []
    for text in selected_texts:
        if 'maker' in _normalize_text(text):
            detail_parts.append('Espaco Maker')
        if 'futsal' in _normalize_text(text):
            detail_parts.append('futsal')
        if 'volei' in _normalize_text(text):
            detail_parts.append('volei escolar')
        if 'biblioteca' in _normalize_text(text):
            detail_parts.append('Biblioteca Aurora')
    unique_details = list(dict.fromkeys(detail_parts))
    if unique_details:
        details_preview = ', '.join(unique_details[:4])
        return (
            f'Hoje a escola divulga atividades e espacos complementares como {details_preview}. '
            f'Se quiser, eu tambem posso detalhar {labels_preview}.'
        )
    return f'Hoje a escola divulga atividades e espacos complementares como {labels_preview}.'


def _direct_required_documents_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    if 'matricula' not in terms or not ({'documentos', 'documento', 'exigidos', 'exigido', 'necessarios'} & terms):
        return None
    doc = _find_first_matching_doc(docs, 'profile.required_documents', ('documentos exigidos',))
    if doc is None or not doc.text.strip():
        return None
    items = [item.strip() for item in doc.text.split(';') if item.strip()]
    if not items:
        return None
    lines = ['Hoje os documentos exigidos para a matricula publicados pela escola sao:']
    lines.extend(f'- {item}' for item in items)
    return '\n'.join(lines)


def _direct_tuition_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    if 'mensalidade' not in terms:
        return None
    preferred_terms = ()
    if {'medio', 'ensino'} & terms:
        preferred_terms = ('ensino medio',)
    elif 'fundamental' in terms:
        preferred_terms = ('ensino fundamental ii',)
    target_doc = None
    if preferred_terms:
        target_doc = _find_first_matching_doc(docs, 'tuition.', preferred_terms)
    if target_doc is None:
        target_doc = _find_first_matching_doc(docs, 'tuition.', ('ensino medio', 'ensino fundamental ii'))
    if target_doc is None:
        return None
    values = re.findall(r'[0-9]+\.[0-9]{2}', target_doc.text)
    monthly_amount = values[0] if values else None
    enrollment_fee = values[1] if len(values) > 1 else None
    if not monthly_amount:
        return None
    segment = target_doc.title
    if enrollment_fee is not None:
        return f'A mensalidade de referencia para {segment} e R$ {monthly_amount}, com taxa de matricula de R$ {enrollment_fee}.'
    return f'A mensalidade de referencia para {segment} e R$ {monthly_amount}.'


def _deterministic_backstop(message: str, plan: PublicPilotPlan | None, docs: list[EvidenceDoc]) -> str | None:
    primary = _select_primary_doc(plan, docs)
    if primary is None:
        return None
    terms = _query_terms(message)
    required_documents_answer = _direct_required_documents_fast_answer(message, docs)
    if required_documents_answer:
        return required_documents_answer
    tuition_answer = _direct_tuition_fast_answer(message, docs)
    if tuition_answer:
        return tuition_answer
    feature_answer = _direct_feature_fast_answer(message, docs)
    if feature_answer:
        return feature_answer
    text = primary.text
    if 'biblioteca' in terms and not any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}):
        library_doc = _find_first_matching_doc(docs, 'feature.', ('biblioteca', 'biblioteca aurora'))
        if library_doc is not None:
            hours_match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', _normalize_text(library_doc.text))
            hours = hours_match.group(0) if hours_match else None
            if hours:
                return f'Sim, a escola tem a {library_doc.title}, com atendimento {hours}.'
            return f'Sim, a escola tem a {library_doc.title}.'
    if any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}) and 'das ' in _normalize_text(text):
        match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', _normalize_text(text))
        hours = match.group(0) if match else None
        if 'biblioteca' in _normalize_text(primary.title):
            return f'A {primary.title} atende ao publico de segunda a sexta, {hours}.' if hours else f'{primary.title}: {text}'
        return text.split('|', 1)[0].strip()
    if any(term in terms for term in {'matricula', 'aulas', 'formatura', 'reuniao'}) and primary.doc_id.startswith('timeline.'):
        return text.split('|', 1)[0].strip()
    if 'instagram' in terms:
        handle = re.search(r'@\w+', primary.text)
        if handle:
            return f'O Instagram institucional e {handle.group(0)}.'
    if {'telefone', 'fax', 'ligo', 'ligar', 'contato'} & terms:
        phone_doc = _find_first_matching_doc(docs, 'contact.', ('telefone', 'phone', 'secretaria'))
        fax_doc = _find_first_matching_doc(docs, 'profile.', ('fax',))
        phone_answer = None
        fax_answer = None
        if phone_doc is not None:
            phone_answer = f"{phone_doc.title}: {phone_doc.text.replace('|', ' ').strip()}"
        if fax_doc is not None and 'nao utiliza fax' in _normalize_text(fax_doc.text):
            fax_answer = 'Hoje a escola nao utiliza fax institucional.'
        if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and 'fax' in terms and phone_answer and fax_answer:
            return f'{phone_answer} {fax_answer}'
        if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and phone_answer:
            return phone_answer
        if 'fax' in terms and fax_answer:
            return fax_answer
    if 'fax' in terms:
        if 'nao utiliza fax' in _normalize_text(primary.text):
            return 'Hoje a escola nao utiliza fax institucional.'
    if any(term in terms for term in {'telefone', 'whatsapp', 'email'}) and primary.doc_id.startswith('contact.'):
        return f"{primary.title}: {primary.text.replace('|', ' ').strip()}"
    return None


def _answer_conflicts_with_backstop(answer_text: str, backstop: str, message: str) -> bool:
    normalized_answer = _normalize_text(answer_text)
    normalized_backstop = _normalize_text(backstop)
    terms = _query_terms(message)
    if not normalized_answer.strip():
        return True
    if any(term in terms for term in {'matricula', 'aulas', 'formatura', 'reuniao'}):
        years = re.findall(r'20\d{2}', normalized_backstop)
        return bool(years) and not any(year in normalized_answer for year in years)
    if any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}):
        hour_tokens = re.findall(r'[0-9]{1,2}h[0-9]{0,2}', normalized_backstop)
        return bool(hour_tokens) and not any(token in normalized_answer for token in hour_tokens)
    if 'instagram' in terms:
        handles = re.findall(r'@\w+', normalized_backstop)
        return bool(handles) and not any(handle in normalized_answer for handle in handles)
    return False


def _is_public_fast_path_query(message: str) -> bool:
    terms = _query_terms(message)
    direct_terms = {
        'horario',
        'hora',
        'abre',
        'fecha',
        'matricula',
        'aulas',
        'formatura',
        'reuniao',
        'instagram',
        'telefone',
        'ligo',
        'ligar',
        'contato',
        'fax',
        'whatsapp',
        'email',
        'site',
        'endereco',
        'biblioteca',
        'telegrama',
        'caixa',
        'postal',
        'documentos',
        'documento',
        'exigidos',
        'necessarios',
        'mensalidade',
        'atividades',
        'atividade',
        'complementares',
        'complementar',
        'oficinas',
        'esportes',
        'maker',
    }
    return bool(terms & direct_terms)


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
    return LLM(
        model=model_name,
        api_key=api_key,
        temperature=0.15,
        max_tokens=700,
    )


def _extract_task_pydantic(task: Any, model_type: type[BaseModel]) -> BaseModel | None:
    output = getattr(task, 'output', None)
    candidate = getattr(output, 'pydantic', None)
    if isinstance(candidate, model_type):
        return candidate
    return None


async def run_public_crewai_pilot(
    *,
    message: str,
    conversation_id: str | None,
    telegram_chat_id: int | None,
    channel: str,
    settings: Any,
) -> dict[str, Any]:
    normalized_message = ' '.join(message.strip().lower().split())
    if Crew is None or Agent is None or Task is None or Process is None:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'crewai_dependency_unavailable',
            'metadata': {
                'slice_name': 'public',
                'normalized_message': normalized_message,
            },
        }

    overall_started_at = perf_counter()
    evidence = await _fetch_public_evidence(settings)
    evidence_docs = _build_evidence_docs(evidence)
    shortlisted_docs = _rank_evidence_docs(message, evidence_docs)
    fast_path_answer = (
        _direct_contact_fast_answer(message, evidence_docs)
        or _direct_contact_fast_answer(message, shortlisted_docs)
        or _direct_feature_fast_answer(message, evidence_docs)
        or _direct_feature_fast_answer(message, shortlisted_docs)
        or _deterministic_backstop(message, None, shortlisted_docs)
    )
    if isinstance(fast_path_answer, str) and fast_path_answer.strip() and _is_public_fast_path_query(message):
        latency_ms = round((perf_counter() - overall_started_at) * 1000, 1)
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_public_fast_path',
            'metadata': {
                'conversation_id': conversation_id or (
                    f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
                ),
                'slice_name': 'public',
                'normalized_message': normalized_message,
                'crewai_installed': True,
                'crewai_version': getattr(crewai_pkg, '__version__', None),
                'agent_roles': [],
                'task_names': [],
                'latency_ms': latency_ms,
                'plan': None,
                'answer': {'answer_text': fast_path_answer, 'citations': [shortlisted_docs[0].doc_id] if shortlisted_docs else []},
                'judge': {'valid': True, 'reason': 'deterministic_fast_path', 'revision_needed': False},
                'evidence_sources': [doc.doc_id for doc in shortlisted_docs],
                'deterministic_backstop_used': True,
            },
        }

    llm = _build_llm(settings)
    if llm is None:
        return {
            'engine_name': 'crewai',
            'executed': False,
            'reason': 'crewai_llm_not_configured',
            'metadata': {
                'slice_name': 'public',
                'normalized_message': normalized_message,
            },
        }
    evidence_bundle = _serialize_evidence_pack(shortlisted_docs)

    planner = Agent(
        role='Public question planner',
        goal='Identify the exact public-school intent, entity, and attribute the user asked about using only the provided shortlisted evidence docs.',
        backstory='You normalize public school questions into a grounded plan before any answer is written. You must prefer concrete source ids over generic guesses.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    composer = Agent(
        role='Grounded answer composer',
        goal='Write a concise, warm, human answer in pt-BR using only the shortlisted evidence docs and the planner context.',
        backstory='You avoid robotic wording, adjacent-domain leakage, and unsupported claims. When the evidence is explicit, answer directly instead of hedging.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )
    judge = Agent(
        role='Answer quality judge',
        goal='Check whether the composed answer actually addressed the asked attribute with the right entity and stayed within the evidence.',
        backstory='You reject answers that sound plausible but answer a neighboring question.',
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=1,
    )

    planning_task = Task(
        name='public_planning',
        description=(
            'Pergunta do usuario: {message}\n'
            'Docs de evidencias publicas mais relevantes:\n{evidence_bundle}\n\n'
            'Retorne um plano estruturado com a intencao principal, entidade, atributo, se precisa de esclarecimento e os ids das fontes mais relevantes.\n'
            'Use apenas os ids dos docs realmente necessarios.\n'
            'Se a pergunta pedir horario, contato, instagram, fax, matricula, inicio das aulas, biblioteca, atividades, estrutura ou endereco, escolha o atributo exato.\n'
            'Se algum doc trouxer um dado literal claro como data, horario, telefone, email, site ou instagram, prefira esse doc especifico no plano.'
        ),
        expected_output='Structured public plan.',
        agent=planner,
        output_pydantic=PublicPilotPlan,
    )
    composition_task = Task(
        name='public_composition',
        description=(
            'Com base na pergunta do usuario, no plano estruturado e nas evidencias publicas, escreva uma resposta curta, natural e calorosa em portugues do Brasil.\n'
            'Nunca invente fatos. Se a evidencia trouxer um horario, data, nome de espaco, telefone, email, instagram, site ou valor, responda diretamente com esse dado.\n'
            'Nao invente datas aproximadas, faixas de periodo ou canais nao citados.\n'
            'Se houver uma data ou horario explicito nos docs selecionados, reproduza esse dado de forma literal na resposta.\n'
            'Se a informacao nao estiver publicada nos docs, diga isso claramente e ofereca o proximo canal adequado.'
        ),
        expected_output='Structured public answer.',
        agent=composer,
        context=[planning_task],
        output_pydantic=PublicPilotAnswer,
    )
    judge_task = Task(
        name='public_judging',
        description=(
            'Revise o plano e a resposta final. Marque como invalida qualquer resposta que troque entidade, atributo ou use um dado nao suportado pelos docs.\n'
            'Se a resposta citar uma data, horario, valor, telefone, instagram, email ou site que nao aparece explicitamente nos docs, marque valid=false.\n'
            'Se estiver boa, marque valid=true.'
        ),
        expected_output='Structured judge result.',
        agent=judge,
        context=[planning_task, composition_task],
        output_pydantic=PublicPilotJudge,
    )

    crew = Crew(
        name='eduassist_public_shadow',
        agents=[planner, composer, judge],
        tasks=[planning_task, composition_task, judge_task],
        process=Process.sequential,
        verbose=False,
        cache=False,
        memory=False,
        tracing=False,
    )

    await asyncio.to_thread(
        crew.kickoff,
        inputs={
            'message': message,
            'evidence_bundle': evidence_bundle,
        },
    )
    latency_ms = round((perf_counter() - overall_started_at) * 1000, 1)

    plan = _extract_task_pydantic(planning_task, PublicPilotPlan)
    answer = _extract_task_pydantic(composition_task, PublicPilotAnswer)
    verdict = _extract_task_pydantic(judge_task, PublicPilotJudge)
    backstop_answer = _deterministic_backstop(message, plan if isinstance(plan, PublicPilotPlan) else None, shortlisted_docs)
    backstop_used = False

    if isinstance(answer, PublicPilotAnswer) and backstop_answer:
        should_apply_backstop = _answer_conflicts_with_backstop(answer.answer_text, backstop_answer, message)
        if isinstance(plan, PublicPilotPlan) and plan.needs_clarification and any(
            term in _query_terms(message) for term in {'telefone', 'fax', 'instagram', 'email', 'site', 'endereco'}
        ):
            should_apply_backstop = True
        if isinstance(verdict, PublicPilotJudge) and not verdict.valid:
            should_apply_backstop = True
        if should_apply_backstop:
            answer = PublicPilotAnswer(answer_text=backstop_answer, citations=[_select_primary_doc(plan if isinstance(plan, PublicPilotPlan) else None, shortlisted_docs).doc_id] if _select_primary_doc(plan if isinstance(plan, PublicPilotPlan) else None, shortlisted_docs) else [])
            verdict = PublicPilotJudge(valid=True, reason='deterministic_backstop_applied', revision_needed=False)
            backstop_used = True

    metadata: dict[str, Any] = {
        'conversation_id': conversation_id or (
            f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
        ),
        'slice_name': 'public',
        'normalized_message': normalized_message,
        'crewai_installed': True,
        'crewai_version': getattr(crewai_pkg, '__version__', None),
        'agent_roles': ['planner', 'composer', 'judge'],
        'task_names': ['public_planning', 'public_composition', 'public_judging'],
        'latency_ms': latency_ms,
        'plan': plan.model_dump(mode='json') if isinstance(plan, PublicPilotPlan) else None,
        'answer': answer.model_dump(mode='json') if isinstance(answer, PublicPilotAnswer) else None,
        'judge': verdict.model_dump(mode='json') if isinstance(verdict, PublicPilotJudge) else None,
        'evidence_sources': [doc.doc_id for doc in shortlisted_docs],
        'deterministic_backstop_used': backstop_used,
    }

    if isinstance(verdict, PublicPilotJudge) and not verdict.valid:
        return {
            'engine_name': 'crewai',
            'executed': True,
            'reason': 'crewai_public_pilot_judge_invalid',
            'metadata': metadata,
        }

    return {
        'engine_name': 'crewai',
        'executed': True,
        'reason': 'crewai_public_pilot_completed',
        'metadata': metadata,
    }
