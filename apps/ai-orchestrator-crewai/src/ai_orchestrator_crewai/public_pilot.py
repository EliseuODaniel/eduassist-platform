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

from .listeners import capture_pilot_events, serialize_pilot_events, suppress_crewai_tracing_messages
from .flow_persistence import build_flow_state_id


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
        if doc.doc_id == 'profile.segments' and any(term in terms for term in ('curriculo', 'curricular', 'base', 'bncc')):
            score += 8
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


def _direct_greeting_fast_answer(message: str) -> str | None:
    normalized = ' '.join(_normalize_text(message).split())
    if normalized in {'oi', 'ola', 'olá', 'bom dia', 'boa tarde', 'boa noite'}:
        return (
            'Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, '
            'matricula, visitas, biblioteca, atividades e rotina escolar.'
        )
    return None


def _direct_comparative_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    if not ({'melhor', 'concorrencia', 'concorrente', 'publica', 'pagar', 'estudar'} & terms):
        return None
    comparative_docs = [doc for doc in docs if doc.doc_id.startswith('highlight.')]
    if not comparative_docs:
        comparative_docs = [doc for doc in docs if doc.doc_id.startswith('feature.')]
    if not comparative_docs:
        return None
    labels = [doc.title for doc in comparative_docs[:2] if doc.title]
    labels_preview = ', '.join(labels) if labels else 'os diferenciais publicados da escola'
    return (
        f'Os diferenciais publicados desta escola hoje incluem {labels_preview}. '
        'Eu nao consigo afirmar que ela seja melhor do que uma concorrente especifica sem fontes comparativas confiaveis, '
        'mas posso te explicar esses diferenciais com clareza.'
    )


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


def _direct_curriculum_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    if not ({'curricular', 'curriculo', 'base', 'bncc'} & terms):
        return None
    segments_doc = next((doc for doc in docs if doc.doc_id == 'profile.segments'), None)
    if segments_doc is None:
        return None
    basis_match = re.search(r'base curricular:\s*([^.;]+)', segments_doc.text, flags=re.IGNORECASE)
    basis = basis_match.group(1).strip() if basis_match else ''
    if not basis:
        return None
    basis = re.sub(r'^\s*a escola segue\s+', '', basis, flags=re.IGNORECASE)
    if {'medio', 'ensino'} & terms:
        return f'No Ensino Medio, a escola segue {basis}.'
    return f'A base curricular publicada pela escola hoje e {basis}.'


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
    greeting_answer = _direct_greeting_fast_answer(message)
    if greeting_answer:
        return greeting_answer
    comparative_answer = _direct_comparative_fast_answer(message, docs)
    if comparative_answer:
        return comparative_answer
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
    curriculum_answer = _direct_curriculum_fast_answer(message, docs)
    if curriculum_answer:
        return curriculum_answer
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
    normalized = ' '.join(_normalize_text(message).split())
    if normalized in {'oi', 'ola', 'olá', 'bom dia', 'boa tarde', 'boa noite'}:
        return True
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
        'curriculo',
        'curricular',
        'base',
        'bncc',
        'atividades',
        'atividade',
        'complementares',
        'complementar',
        'oficinas',
        'esportes',
        'maker',
        'melhor',
        'concorrencia',
        'concorrente',
        'publica',
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
    from .public_flow import PublicShadowFlow

    flow = PublicShadowFlow(settings=settings)
    with suppress_crewai_tracing_messages():
        result = await flow.kickoff_async(
            inputs={
                'id': build_flow_state_id(
                    slice_name='public',
                    conversation_id=conversation_id or (
                        f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
                    ),
                    telegram_chat_id=telegram_chat_id,
                    channel=channel,
                ),
                'message': message,
                'conversation_id': conversation_id or (
                    f'telegram:{telegram_chat_id}' if channel == 'telegram' and telegram_chat_id is not None else None
                ),
                'telegram_chat_id': telegram_chat_id,
                'channel': channel,
            }
        )
    return result if isinstance(result, dict) else {
        'engine_name': 'crewai',
        'executed': False,
        'reason': 'crewai_public_flow_unexpected_output',
        'metadata': {
            'slice_name': 'public',
            'output_type': type(result).__name__,
        },
    }
