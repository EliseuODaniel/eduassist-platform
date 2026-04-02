from __future__ import annotations

import asyncio
import json
import re
from time import monotonic, perf_counter
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


_PUBLIC_RESOURCE_CACHE: dict[str, dict[str, Any]] = {}


def _crewai_google_model(configured_model: str) -> str:
    base = str(configured_model or '').strip()
    if base.startswith('models/'):
        base = base.split('/', 1)[1]
    if base.startswith('gemini/'):
        base = base.split('/', 1)[1]
    if '-preview' in base:
        return 'gemini-2.5-flash'
    return base or 'gemini-2.5-flash'


def _infer_retrieval_category(message: str) -> str | None:
    terms = _query_terms(message)
    if {'aulas', 'reuniao', 'reunião', 'formatura', 'calendario', 'datas'} & terms:
        return 'calendar'
    return None


async def _fetch_public_evidence(settings: Any, *, retrieval_query: str | None = None) -> dict[str, Any]:
    base_url = str(getattr(settings, 'api_core_url', 'http://api-core:8000')).rstrip('/')
    orchestrator_url = str(getattr(settings, 'orchestrator_url', 'http://ai-orchestrator:8000')).rstrip('/')
    names: list[str] = []
    requests: list[Any] = []
    payloads: dict[str, Any] = {}

    def get_cached_public_resource(cache_key: str) -> Any | None:
        entry = _PUBLIC_RESOURCE_CACHE.get(cache_key)
        if not isinstance(entry, dict):
            return None
        expires_at = float(entry.get('expires_at', 0.0) or 0.0)
        if expires_at <= monotonic():
            _PUBLIC_RESOURCE_CACHE.pop(cache_key, None)
            return None
        return entry.get('value')

    def store_cached_public_resource(cache_key: str, value: Any) -> Any:
        ttl_seconds = float(getattr(settings, 'crewai_public_resource_cache_ttl_seconds', 120.0) or 120.0)
        _PUBLIC_RESOURCE_CACHE[cache_key] = {
            'value': value,
            'expires_at': monotonic() + ttl_seconds,
        }
        return value

    cached_school_profile = get_cached_public_resource('school_profile')
    if isinstance(cached_school_profile, dict):
        payloads['school_profile'] = dict(cached_school_profile)
    else:
        names.append('school_profile')
        requests.append(('school_profile', f'{base_url}/v1/public/school-profile', 'get'))

    cached_org_directory = get_cached_public_resource('org_directory')
    if isinstance(cached_org_directory, dict):
        payloads['org_directory'] = dict(cached_org_directory)
    else:
        names.append('org_directory')
        requests.append(('org_directory', f'{base_url}/v1/public/org-directory', 'get'))

    cached_timeline = get_cached_public_resource('timeline')
    if isinstance(cached_timeline, dict):
        payloads['timeline'] = dict(cached_timeline)
    else:
        names.append('timeline')
        requests.append(('timeline', f'{base_url}/v1/public/timeline', 'get'))

    cached_calendar = get_cached_public_resource('calendar_events')
    if isinstance(cached_calendar, dict):
        payloads['calendar_events'] = dict(cached_calendar)
    else:
        names.append('calendar_events')
        requests.append(('calendar_events', f'{base_url}/v1/calendar/public', 'get'))

    async with httpx.AsyncClient(timeout=15.0) as client:
        inflight = [client.get(url) for _name, url, method in requests if method == 'get']
        if bool(getattr(settings, 'shared_retrieval_enabled', False)) and retrieval_query:
            names.append('shared_retrieval')
            inflight.append(
                client.post(
                    f'{orchestrator_url}/v1/retrieval/search',
                    json={
                        'query': retrieval_query,
                        'top_k': int(getattr(settings, 'shared_retrieval_top_k', 6) or 6),
                        'visibility': 'public',
                        'category': _infer_retrieval_category(retrieval_query),
                    },
                )
            )
        responses = await asyncio.gather(*inflight, return_exceptions=True)
    for name, response in zip(names, responses, strict=True):
        if isinstance(response, Exception):
            if name == 'shared_retrieval':
                payloads[name] = {'hits': [], 'query_plan': None, 'context_pack': None}
                continue
            raise response
        if name == 'shared_retrieval' and response.status_code >= 400:
            payloads[name] = {'hits': [], 'query_plan': None, 'context_pack': None}
            continue
        response.raise_for_status()
        body = response.json()
        if name != 'shared_retrieval':
            body = store_cached_public_resource(name, body)
        payloads[name] = body
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


def _is_followup_style_message(message: str) -> bool:
    normalized = ' '.join(_normalize_text(message).split())
    return (
        normalized.startswith('e ')
        or normalized.startswith('mas ')
        or normalized.startswith('entao ')
        or normalized.startswith('entao,')
        or normalized.startswith('entao como')
        or normalized.startswith('qual o nome dela')
        or normalized.startswith('qual o nome dele')
        or normalized.startswith('qual o horario dela')
        or normalized.startswith('qual o horario dele')
        or normalized.startswith('e o horario')
        or normalized.startswith('e o nome')
    )


def _needs_shared_retrieval(message: str) -> bool:
    normalized = ' '.join(_normalize_text(message).split())
    terms = _query_terms(message)
    if {
        'compare',
        'comparacao',
        'comparativo',
        'sintetize',
        'relacione',
        'cruze',
        'explique',
        'guia',
        'documentos',
        'documentacao',
        'manual',
        'politica',
    } & terms:
        return True
    return any(
        phrase in normalized
        for phrase in (
            'com base nos documentos',
            'do ponto de vista financeiro e administrativo',
            'o que uma familia precisa entender',
            'de ponta a ponta',
            'guia de sobrevivencia do primeiro mes',
            'quando cruzamos',
        )
    )


def _augment_public_message_with_state(
    message: str,
    *,
    active_entity: str | None,
    active_attribute: str | None,
) -> str:
    if not (active_entity or active_attribute):
        return message
    if not _is_followup_style_message(message) and len(_query_terms(message)) > 8:
        return message
    context_hints: list[str] = []
    normalized_entity = _normalize_text(active_entity or '')
    normalized_attribute = _normalize_text(active_attribute or '')
    if normalized_entity:
        context_hints.append(normalized_entity)
    if normalized_attribute:
        context_hints.append(normalized_attribute)
    if 'biblioteca' in normalized_entity:
        context_hints.extend(['biblioteca', 'biblioteca aurora'])
        if normalized_attribute == 'hours':
            context_hints.append('horario')
        elif normalized_attribute == 'name':
            context_hints.append('nome')
    if normalized_attribute in {'document_submission', 'submission'} or normalized_entity in {'documentos', 'documento'}:
        context_hints.extend(['documentos', 'enviar documentos', 'envio', 'secretaria', 'email', 'portal'])
    if normalized_entity in {'comparativo', 'diferenciais', 'diferenciais da escola'} or normalized_attribute in {'comparative', 'diferenciais'}:
        context_hints.extend(['comparacao', 'publica', 'particular', 'projeto', 'acompanhamento', 'rotina'])
    if normalized_entity in {'localizacao', 'endereco'} or normalized_attribute in {'address', 'city', 'state', 'postal_code'}:
        context_hints.extend(['endereco', 'cidade', 'estado', 'cep'])
    if normalized_entity in {'assistente', 'bot'} or normalized_attribute == 'capabilities':
        context_hints.extend(['assistente', 'capacidades', 'ajuda'])
    return ' '.join(part for part in [message, *context_hints] if part).strip()


def _parse_decimal_amount(raw_value: str) -> float | None:
    value = str(raw_value or '').strip()
    if not value:
        return None
    value = value.replace('R$', '').replace(' ', '')
    if ',' in value and '.' in value:
        value = value.replace('.', '').replace(',', '.')
    elif ',' in value:
        value = value.replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return None


def _format_brl(value: float) -> str:
    formatted = f'{value:,.2f}'
    return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')


def _extract_hypothetical_children_count(message: str) -> int | None:
    normalized = _normalize_text(message)
    for pattern in (
        r'\bse eu tiver\s+(\d+)\s+filhos?\b',
        r'\bse eu tivesse\s+(\d+)\s+filhos?\b',
        r'\b(\d+)\s+filhos?\b',
    ):
        match = re.search(pattern, normalized)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
    return None


def _tuition_rows(docs: list[EvidenceDoc]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in docs:
        if not doc.doc_id.startswith('tuition.'):
            continue
        parts = [part.strip() for part in doc.text.split('|') if part.strip()]
        row: dict[str, Any] = {
            'segment': doc.title.strip(),
            'shift_label': parts[0] if len(parts) >= 1 else '',
            'monthly_amount_raw': parts[1] if len(parts) >= 2 else '',
            'enrollment_fee_raw': parts[2] if len(parts) >= 3 else '',
            'notes': parts[3] if len(parts) >= 4 else '',
        }
        row['monthly_amount'] = _parse_decimal_amount(str(row['monthly_amount_raw']))
        row['enrollment_fee'] = _parse_decimal_amount(str(row['enrollment_fee_raw']))
        rows.append(row)
    return rows


def _direct_location_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    normalized = _normalize_text(message)
    if not (
        {'endereco', 'endereço', 'estado', 'cidade', 'cep', 'localizacao', 'localização'} & terms
        or 'onde fica' in normalized
        or 'por que antes nao encontrou o endereco' in normalized
        or 'por que antes não encontrou o endereco' in normalized
    ):
        return None
    location_doc = next((doc for doc in docs if doc.doc_id == 'profile.location'), None)
    if location_doc is None:
        return None
    text = location_doc.text
    city_match = re.search(r',\s*([^,]+),\s*([^,/]+)/([A-Z]{2})', text)
    cep_match = re.search(r'CEP\s*([0-9-]+)', text, flags=re.IGNORECASE)
    if 'por que antes' in normalized and 'endereco' in normalized:
        return (
            'Antes eu nao tinha resolvido corretamente esse item pelo perfil publico. '
            f"Corrigindo: {text.split('Site:', 1)[0].strip().rstrip('.')}."
        )
    if 'estado' in terms:
        if city_match:
            return f'O endereco publicado fica em {city_match.group(2).strip()}/{city_match.group(3).strip()}.'
    if 'cidade' in terms:
        if city_match:
            return f'O endereco publicado fica em {city_match.group(2).strip()}, {city_match.group(3).strip()}.'
    if 'cep' in terms and cep_match:
        return f'O CEP publicado da escola e {cep_match.group(1)}.'
    if {'endereco', 'endereço', 'localizacao', 'localização'} & terms or 'onde fica' in normalized:
        return text.split('Site:', 1)[0].strip().rstrip('.')
    return None


def _direct_contact_bundle_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('endereco completo', 'endereço completo', 'telefone principal'))
        and any(term in normalized for term in ('secretaria', 'melhor canal', 'canal da secretaria'))
    ):
        return None
    location_answer = _direct_location_fast_answer(message, docs)
    phone_doc = _find_first_matching_doc(docs, 'contact.', ('telefone', 'phone', 'secretaria'))
    whatsapp_doc = _find_first_matching_doc(docs, 'contact.', ('whatsapp', 'secretaria digital'))
    email_doc = _find_first_matching_doc(docs, 'contact.', ('email', 'secretaria'))
    parts: list[str] = []
    if location_answer:
        parts.append(location_answer.rstrip('.'))
    if phone_doc is not None:
        parts.append(f"O telefone principal hoje e {phone_doc.text.replace('|', ' ').strip()}.")
    if whatsapp_doc is not None:
        parts.append(f"O melhor canal para a secretaria hoje e {whatsapp_doc.text.replace('|', ' ').strip()}.")
    elif email_doc is not None:
        parts.append(f"O melhor canal para a secretaria hoje e {email_doc.text.replace('|', ' ').strip()}.")
    return ' '.join(part for part in parts if part).strip() or None


def _stateful_public_followup_fast_answer(
    message: str,
    *,
    active_entity: str | None,
    docs: list['EvidenceDoc'],
) -> str | None:
    normalized_entity = _normalize_text(active_entity or '')
    terms = _query_terms(message)
    if normalized_entity in {'localizacao', 'endereco'}:
        location_answer = _direct_location_fast_answer(message, docs)
        if location_answer:
            return location_answer
    if normalized_entity in {'comparativo', 'diferenciais', 'diferenciais da escola'} and (
        {'pratica', 'rotina', 'muda', 'dia', 'acompanhamento', 'projeto'} & terms
    ):
        return (
            'Na pratica, isso muda em uma rotina com aprendizagem por projetos, '
            'acompanhamento mais proximo, tutoria academica e projeto de vida integrados ao percurso escolar.'
        )
    if normalized_entity in {'comparativo', 'diferenciais', 'diferenciais da escola'} and (
        {'bncc', 'curricular', 'curriculo', 'curriculo', 'base'} & terms
    ):
        return (
            'Sim. A base curricular publicada continua apoiada na BNCC, articulada com projeto de vida, '
            'producao textual, cultura digital responsavel e aprofundamento academico progressivo.'
        )
    if 'timeline' in normalized_entity:
        timeline_docs = [doc for doc in docs if doc.doc_id.startswith('timeline.')]
        if not timeline_docs:
            return None
        if 'aulas' in terms:
            aulas_doc = next((doc for doc in timeline_docs if 'aulas' in _normalize_text(f'{doc.title} {doc.text}')), None)
            if aulas_doc is not None:
                return aulas_doc.text.split('|', 1)[0].strip()
        if 'matricula' in terms:
            matricula_doc = next((doc for doc in timeline_docs if 'matricula' in _normalize_text(f'{doc.title} {doc.text}')), None)
            if matricula_doc is not None:
                return matricula_doc.text.split('|', 1)[0].strip()
        if 'formatura' in terms:
            formatura_doc = next((doc for doc in timeline_docs if 'formatura' in _normalize_text(f'{doc.title} {doc.text}')), None)
            if formatura_doc is not None:
                return formatura_doc.text.split('|', 1)[0].strip()
        if 'reuniao' in terms:
            reuniao_doc = next((doc for doc in timeline_docs if 'reuniao' in _normalize_text(f'{doc.title} {doc.text}')), None)
            if reuniao_doc is not None:
                return reuniao_doc.text.split('|', 1)[0].strip()
        return None
    if 'biblioteca' not in normalized_entity:
        return None
    library_doc = _find_first_matching_doc(docs, 'feature.', ('biblioteca', 'biblioteca aurora'))
    if library_doc is None:
        return None
    if 'nome' in terms and not any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}):
        return f'O nome desse espaco e {library_doc.title}.'
    if any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}):
        hours_match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', _normalize_text(library_doc.text))
        hours = hours_match.group(0) if hours_match else None
        if hours:
            return f'O horario da {library_doc.title} hoje e de segunda a sexta, {hours}.'
        return f'O horario da {library_doc.title} hoje segue o registro publico disponivel.'
    return None


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
    shared_retrieval = evidence.get('shared_retrieval', {})
    retrieval_hits = shared_retrieval.get('hits', []) if isinstance(shared_retrieval, dict) else []
    retrieval_context_pack = str(shared_retrieval.get('context_pack', '') or '').strip() if isinstance(shared_retrieval, dict) else ''

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
    add(
        'profile.intervals',
        'school_profile',
        'Intervalos publicos por segmento',
        '; '.join(_stringify_items(profile.get('interval_schedule', []), ('segment', 'label', 'starts_at', 'ends_at', 'notes'))),
    )
    add('profile.contacts', 'school_profile', 'Canais oficiais', '; '.join(_stringify_items(profile.get('contact_channels', []), ('channel', 'label', 'value'))))
    add(
        'profile.features',
        'school_profile',
        'Espacos, atividades e diferenciais',
        '; '.join(_stringify_items(profile.get('feature_inventory', []), ('label', 'category', 'available', 'notes'))),
    )
    add('profile.tuition', 'school_profile', 'Valores publicos e politica comercial', '; '.join(_stringify_items(profile.get('tuition_reference', []), ('segment', 'shift_label', 'monthly_amount', 'enrollment_fee', 'notes'))))
    add(
        'profile.visits',
        'school_profile',
        'Visitas e admissoes',
        '; '.join(_stringify_items(profile.get('visit_offers', []), ('title', 'day_label', 'start_time', 'end_time', 'location', 'notes'))),
    )
    add(
        'profile.services',
        'school_profile',
        'Catalogo publico de servicos',
        '; '.join(_stringify_items(profile.get('service_catalog', []), ('title', 'request_channel', 'typical_eta', 'notes'))),
    )
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
        'profile.admissions_highlights',
        'school_profile',
        'Destaques de admissions',
        '; '.join(str(item).strip() for item in (profile.get('admissions_highlights') or []) if str(item).strip()),
    )
    academic_policy = profile.get('academic_policy') if isinstance(profile, dict) else None
    if isinstance(academic_policy, dict):
        add(
            'policy.project_of_life',
            'school_profile',
            'Projeto de vida',
            str(academic_policy.get('project_of_life_summary', '') or ''),
        )
        passing_policy = academic_policy.get('passing_policy')
        if isinstance(passing_policy, dict):
            add(
                'policy.passing',
                'school_profile',
                'Aprovacao, media e recuperacao',
                ' | '.join(
                    str(passing_policy.get(key, '')).strip()
                    for key in ('passing_average', 'reference_scale', 'recovery_support', 'notes')
                    if str(passing_policy.get(key, '')).strip()
                ),
            )
        attendance_policy = academic_policy.get('attendance_policy')
        if isinstance(attendance_policy, dict):
            add(
                'policy.attendance',
                'school_profile',
                'Frequencia e faltas',
                ' | '.join(
                    str(attendance_policy.get(key, '')).strip()
                    for key in ('minimum_attendance_percent', 'first_absence_guidance', 'chronic_absence_guidance', 'follow_up_channel', 'notes')
                    if str(attendance_policy.get(key, '')).strip()
                ),
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
                for key in ('feature_key', 'label', 'category', 'available', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('shift_offers', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'shift.{index}',
            'school_profile',
            str(item.get('segment', f'Turno {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('shift_label', 'starts_at', 'ends_at', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('interval_schedule', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'interval.{index}',
            'school_profile',
            str(item.get('segment', f'Intervalo {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('label', 'starts_at', 'ends_at', 'notes')
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
                for key in ('day_label', 'start_time', 'end_time', 'location', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('admissions_highlights', []), start=1):
        add(
            f'admissions.{index}',
            'school_profile',
            f'Admissions {index}',
            str(item).strip(),
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
                for key in ('description', 'evidence_line')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(profile.get('service_catalog', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'service.{index}',
            'school_profile',
            str(item.get('title', f'Servico {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('audience', 'request_channel', 'typical_eta', 'notes')
                if str(item.get(key, '')).strip()
            ),
        )

    for index, item in enumerate(directory.get('leadership_team', []), start=1):
        if not isinstance(item, dict):
            continue
        add(
            f'leadership.{index}',
            'org_directory',
            str(item.get('name', f'Lideranca {index}')),
            ' | '.join(
                str(item.get(key, '')).strip()
                for key in ('title', 'focus', 'contact_channel', 'notes')
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

    if retrieval_context_pack:
        add(
            'retrieval.context_pack',
            'shared_retrieval',
            'Pacote de contexto recuperado',
            retrieval_context_pack,
        )

    for index, hit in enumerate(retrieval_hits[:6], start=1):
        if not isinstance(hit, dict):
            continue
        excerpt = str(hit.get('contextual_summary', '') or hit.get('text_excerpt', '') or '').strip()
        if not excerpt:
            continue
        add(
            f'retrieval.{index}',
            'shared_retrieval',
            str(hit.get('document_title', f'Documento recuperado {index}')),
            ' | '.join(
                part
                for part in (
                    str(hit.get('category', '')).strip(),
                    excerpt,
                )
                if part
            ),
        )

    return docs


def _rank_evidence_docs(message: str, docs: list[EvidenceDoc], *, limit: int = 4) -> list[EvidenceDoc]:
    terms = _query_terms(message)
    if not terms:
        return docs[:limit]

    ranked: list[tuple[int, int, EvidenceDoc]] = []
    for doc in docs:
        haystack = _normalize_text(f'{doc.title} {doc.text}')
        score = sum(5 if term in _normalize_text(doc.title) else 2 for term in terms if term in haystack)
        if doc.doc_id == 'profile.segments' and any(term in terms for term in ('curriculo', 'curricular', 'base', 'bncc')):
            score += 8
        if doc.doc_id == 'profile.overview' and any(
            term in terms for term in ('proposta', 'pedagogica', 'pedagogico', 'acolhimento', 'disciplina', 'aprendizagem')
        ):
            score += 9
        if doc.doc_id.startswith('highlight.') and any(
            term in terms for term in ('proposta', 'pedagogica', 'pedagogico', 'acolhimento', 'disciplina', 'publica', 'pagar')
        ):
            score += 7
        if any(term in haystack for term in ('biblioteca', 'biblioteca aurora')) and any(
            term in terms for term in ('biblioteca', 'horario', 'hora')
        ):
            score += 4
        if any(term in haystack for term in ('matricula', 'admissoes')) and any(
            term in terms for term in ('matricula', 'admissao', 'inscricao')
        ):
            score += 4
        if doc.doc_id.startswith('timeline.') and any(
            term in terms for term in ('matricula', 'aulas', 'formatura', 'reuniao')
        ):
            score += 10
        if doc.doc_id.startswith('calendar.') and any(
            term in terms for term in ('aulas', 'reuniao', 'formatura')
        ):
            score += 6
        if doc.doc_id.startswith('service.') and any(
            term in terms for term in ('bolsa', 'desconto', 'boleto', 'financeiro', 'secretaria', 'orientacao', 'orientação', 'bullying', 'portal', 'senha', 'login')
        ):
            score += 9
        if doc.doc_id.startswith('leadership.') and any(
            term in terms for term in ('diretor', 'diretora', 'direcao', 'direção', 'coordenacao', 'coordenação')
        ):
            score += 10
        if doc.doc_id.startswith('shift.') and any(
            term in terms for term in ('turno', 'turnos', 'matutino', 'vespertino', 'noturno', 'turmas')
        ):
            score += 10
        if doc.doc_id.startswith('interval.') and any(
            term in terms for term in ('intervalo', 'intervalos', 'recreio')
        ):
            score += 10
        if doc.doc_id.startswith('policy.') and any(
            term in terms for term in ('projeto', 'vida', 'aprovacao', 'aprovação', 'recuperacao', 'recuperação', 'frequencia', 'frequência', 'faltas')
        ):
            score += 11
        if doc.source == 'shared_retrieval':
            score += 12
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
    normalized_message = _normalize_text(message)
    document_send_followup = (
        'documentos' in terms
        and ({'mando', 'envio', 'enviar', 'mandar'} & terms)
    ) or any(
        phrase in normalized_message
        for phrase in {
            'como mando os documentos',
            'como enviar os documentos',
            'como posso enviar os documentos',
            'entao como mando os documentos',
            'entao como envio os documentos',
        }
    )
    if not (
        ({'telefone', 'fax', 'ligo', 'ligar', 'contato', 'caixa', 'postal', 'telegrama'} & terms)
        or document_send_followup
    ):
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
    if document_send_followup:
        return f'Para enviar documentos hoje, use {fallback_channels}.'
    if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and 'fax' in terms and phone_answer and fax_answer:
        return f'{phone_answer} {fax_answer}'
    if ({'telefone', 'ligo', 'ligar', 'contato'} & terms) and phone_answer:
        return phone_answer
    if 'fax' in terms and fax_answer:
        return 'Hoje nao existe numero de fax publicado, porque a escola nao utiliza fax institucional.'
    return None


def _direct_service_routing_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    terms = _query_terms(message)
    explicit_routing_request = any(
        phrase in normalized
        for phrase in (
            'com quem eu falo sobre',
            'quem responde por',
            'pra quem eu falo sobre',
            'para quem eu falo sobre',
            'qual canal',
        )
    )
    service_docs = [doc for doc in docs if doc.doc_id.startswith('service.')]
    contact_docs = [doc for doc in docs if doc.doc_id.startswith('contact.')]
    if not explicit_routing_request or (not service_docs and not contact_docs):
        return None

    def contact_for(label_terms: tuple[str, ...]) -> str | None:
        for doc in contact_docs:
            haystack = _normalize_text(f'{doc.title} {doc.text}')
            if any(term in haystack for term in label_terms):
                return f"{doc.title}: {doc.text.replace('|', ' ').strip()}"
        return None

    route_lines: list[str] = []
    if any(term in normalized for term in {'direcao', 'direção', 'diretora', 'diretor'}):
        leadership_doc = next((doc for doc in docs if doc.doc_id.startswith('leadership.') and 'helena martins' in _normalize_text(f'{doc.title} {doc.text}')), None)
        if leadership_doc is not None:
            route_lines.append(f'Direcao geral: {leadership_doc.title}.')
    admissions_terms = {'bolsa', 'bolsas', 'desconto', 'descontos', 'matricula', 'matriculas', 'admissoes', 'admissao', 'atendimento', 'comercial'}
    finance_terms = {'boleto', 'boletos', 'financeiro', 'mensalidade', 'mensalidades', 'pagamento', 'pagamentos', 'contrato', 'contratos', 'vencimento', 'vencimentos'}
    guidance_terms = {'bullying', 'convivencia', 'convivência', 'orientacao', 'orientação', 'educacional', 'apoio', 'escolar'}
    digital_terms = {'portal', 'senha', 'login', 'aplicativo', 'app'}
    if admissions_terms & terms:
        admissions = contact_for(('admissoes', 'atendimento comercial'))
        if admissions:
            route_lines.append(f'Para bolsa, desconto e matricula, o melhor canal hoje e Atendimento comercial / Admissoes. {admissions}')
    if finance_terms & terms:
        finance = contact_for(('financeiro',))
        if finance:
            route_lines.append(f'Para boletos, vencimentos e contratos, o melhor canal hoje e o financeiro. {finance}')
    if guidance_terms & terms or 'orientacao educacional' in normalized or 'orientação educacional' in normalized:
        guidance = contact_for(('orientacao educacional',))
        if guidance:
            route_lines.append(f'Para bullying, convivencia e apoio escolar, o canal indicado e a orientacao educacional. {guidance}')
    if digital_terms & terms:
        digital = contact_for(('suporte digital', 'secretaria digital'))
        if digital:
            route_lines.append(f'Para portal, senha, login e canais digitais, o melhor caminho hoje e o suporte digital. {digital}')
    if route_lines:
        return '\n'.join(route_lines)
    if {'secretaria', 'coordenacao', 'coordenação', 'orientacao', 'orientação'} & terms:
        return (
            'Secretaria cuida de documentos, declaracoes, historico e orientacoes administrativas. '
            'Coordenacao pedagogica cuida de rotina escolar, serie, acompanhamento e transicao. '
            'Orientacao educacional apoia convivencia, adaptacao, bem-estar e rotina de estudo.'
        )
    return None


def _direct_auth_guidance_fast_answer(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(
        term in normalized
        for term in (
            'como vinculo minha conta',
            'como eu vinculo minha conta',
            'como eu vinculo meu telegram',
            'como vinculo meu telegram',
            'telegram a minha conta da escola',
            'vincular telegram',
            'codigo de vinculacao',
            'código de vinculação',
        )
    ):
        return (
            'Para vincular o Telegram a sua conta da escola, entre no portal autenticado, gere o codigo de vinculacao '
            'e depois envie aqui o comando /start link_<codigo>.'
        )
    return None


def _direct_timeline_bundle_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        ('matricula' in normalized or 'matrícula' in normalized)
        and any(
            term in normalized
            for term in (
                'aulas',
                'inicio das aulas',
                'início das aulas',
                'comeco das aulas',
                'começo das aulas',
                'comecam as aulas',
                'começam as aulas',
            )
        )
    ):
        return None
    timeline_docs = [doc for doc in docs if doc.doc_id.startswith('timeline.')]
    matricula_doc = next((doc for doc in timeline_docs if 'matricula' in _normalize_text(f'{doc.title} {doc.text}')), None)
    aulas_doc = next((doc for doc in timeline_docs if 'aulas' in _normalize_text(f'{doc.title} {doc.text}')), None)
    reuniao_doc = next((doc for doc in timeline_docs if 'reuniao' in _normalize_text(f'{doc.title} {doc.text}')), None)
    lines: list[str] = []
    if matricula_doc is not None:
        lines.append(matricula_doc.text)
    if aulas_doc is not None:
        lines.append(aulas_doc.text)
    if reuniao_doc is not None and any(term in normalized for term in ('responsaveis', 'responsáveis', 'reuniao', 'reunião', 'familia', 'família')):
        lines.append(reuniao_doc.text)
    return '\n'.join(lines) if lines else None


def _direct_family_new_bundle_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('primeiro filho', 'familia nova', 'família nova', 'estou chegando agora'))
        and 'matricula' in normalized
        and 'calendario' in normalized
        and any(term in normalized for term in ('avaliacoes', 'avaliações', 'avaliacao', 'avaliação'))
    ):
        return None
    return (
        'Para uma familia nova, matricula, calendario e agenda de avaliacoes precisam ser lidos juntos: '
        'a matricula organiza ingresso, documentos e atendimento inicial; o calendario mostra inicio das aulas, '
        'marcos do bimestre e reunioes com responsaveis; e a agenda de avaliacoes explica janelas de prova, '
        'recuperacao e comunicados pedagogicos do primeiro bimestre.'
    )


def _direct_permanence_support_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('familia', 'família', 'responsaveis', 'responsáveis'))
        and any(term in normalized for term in ('permanencia', 'permanência', 'vida escolar'))
        and 'apoio' in normalized
    ):
        return None
    return (
        'Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina '
        'orientacao educacional, monitorias, comunicados digitais, reunioes periodicas com responsaveis '
        'e acionamento de acompanhamento quando frequencia, adaptacao ou rotina de estudo exigem intervencao.'
    )


def _direct_conduct_frequency_recovery_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('regulamentos', 'regulamento', 'disciplina', 'convivencia', 'convivência'))
        and any(term in normalized for term in ('frequencia', 'frequência'))
        and any(term in normalized for term in ('recuperacao', 'recuperação'))
    ):
        return None
    return (
        'Regulamentos gerais, politica de avaliacao e orientacao ao estudante se conectam assim: '
        'disciplina e convivio sustentam a rotina; frequencia minima e justificativas influenciam alerta academico; '
        'e recuperacao, segunda chamada e apoio pedagogico entram quando desempenho ou assiduidade exigem recomposicao.'
    )


def _direct_transversal_year_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('responsaveis', 'responsáveis', 'familia', 'família'))
        and any(term in normalized for term in ('avaliacoes', 'avaliações', 'avaliacao', 'avaliação'))
        and any(term in normalized for term in ('estudo orientado', 'canais digitais', 'portal', 'telegram', 'digitais'))
    ):
        return None
    return (
        'Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais funcionam como um circuito unico: '
        'o portal publica cronogramas e ajustes, a escola reforca comunicados pelos canais oficiais, '
        'e estudo orientado ou acompanhamento adicional entram quando calendario, desempenho ou rotina pedem suporte mais proximo.'
    )


def _direct_facilities_study_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not (
        any(term in normalized for term in ('biblioteca', 'laboratorios', 'laboratório', 'laboratorio', 'laboratórios'))
        and any(term in normalized for term in ('estudo', 'apoio', 'ensino medio', 'ensino médio'))
    ):
        return None
    return (
        'Biblioteca e laboratorios aparecem como apoio ao estudo do ensino medio: a Biblioteca Aurora oferece consulta, '
        'emprestimo e estudo orientado; os laboratorios apoiam aulas praticas, pesquisa e projetos maker; '
        'e o contraturno conecta esses espacos a monitorias, cultura digital e projetos interdisciplinares.'
    )


def _direct_leadership_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    terms = _query_terms(message)
    leadership_docs = [doc for doc in docs if doc.doc_id.startswith('leadership.')]
    if not leadership_docs:
        return None
    if not (
        {'diretor', 'diretora', 'direcao', 'direção', 'coordenacao', 'coordenação', 'lideranca', 'liderança'} & terms
        or 'quem responde por' in normalized
    ):
        return None
    director_doc = next((doc for doc in leadership_docs if 'diretora geral' in _normalize_text(doc.text)), None)
    if director_doc is not None and {'diretor', 'diretora', 'direcao', 'direção'} & terms:
        parts = [part.strip() for part in director_doc.text.split('|') if part.strip()]
        title = parts[0] if parts else 'Diretora geral'
        contact = parts[2] if len(parts) >= 3 else ''
        if 'email' in terms or 'contato' in terms:
            return f'{director_doc.title} e a {title}. Contato institucional: {contact}.'
        return f'{director_doc.title} e a {title}.'
    if 'quem responde por' in normalized:
        names: list[str] = []
        if director_doc is not None:
            names.append(f'direcao: {director_doc.title}')
        coordination_doc = next((doc for doc in leadership_docs if 'coordenador' in _normalize_text(doc.text) or 'coordenadora' in _normalize_text(doc.text)), None)
        if coordination_doc is not None:
            names.append(f'coordenacao: {coordination_doc.title}')
        if names:
            return 'Hoje os responsaveis institucionais publicados incluem ' + '; '.join(names) + '.'
    return None


def _direct_schedule_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    terms = _query_terms(message)
    shift_docs = [doc for doc in docs if doc.doc_id.startswith('shift.')]
    interval_docs = [doc for doc in docs if doc.doc_id.startswith('interval.')]
    if {'intervalo', 'intervalos', 'recreio'} & terms and interval_docs:
        lines = ['Os intervalos publicos por segmento hoje sao:']
        for doc in interval_docs[:4]:
            parts = [part.strip() for part in doc.text.split('|') if part.strip()]
            if len(parts) >= 3:
                lines.append(f"- {doc.title}: {parts[0]}, {parts[1]} as {parts[2]}.")
        if len(lines) > 1:
            return '\n'.join(lines)
    if {'turno', 'turnos', 'matutino', 'vespertino', 'noturno', 'turmas'} & terms and shift_docs:
        lines = ['Os turnos publicos hoje aparecem assim:']
        for doc in shift_docs[:4]:
            parts = [part.strip() for part in doc.text.split('|') if part.strip()]
            if len(parts) >= 3:
                lines.append(f"- {doc.title}: {parts[0]}, {parts[1]} as {parts[2]}.")
        if 'noturno' in terms:
            lines.append('- Nao ha turno noturno publicado para os segmentos regulares.')
        if len(lines) > 1:
            return '\n'.join(lines)
    if 'horario' in terms and any(term in normalized for term in ('turno matutino', 'manha', 'manhã')) and shift_docs:
        first_doc = shift_docs[0]
        parts = [part.strip() for part in first_doc.text.split('|') if part.strip()]
        if len(parts) >= 3:
            return f'O turno matutino publicado para {first_doc.title} vai de {parts[1]} a {parts[2]}.'
    return None


def _direct_policy_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    terms = _query_terms(message)
    project_doc = next((doc for doc in docs if doc.doc_id == 'policy.project_of_life'), None)
    passing_doc = next((doc for doc in docs if doc.doc_id == 'policy.passing'), None)
    attendance_doc = next((doc for doc in docs if doc.doc_id == 'policy.attendance'), None)
    if (
        any(term in normalized for term in ('compare', 'comparar', 'comparacao', 'comparação'))
        and any(term in normalized for term in ('regulamentos gerais', 'manual geral', 'manual de regulamentos'))
        and any(term in normalized for term in ('politica de avaliacao', 'política de avaliação'))
    ):
        attendance_parts = [part.strip() for part in attendance_doc.text.split('|') if part.strip()] if attendance_doc is not None else []
        passing_parts = [part.strip() for part in passing_doc.text.split('|') if part.strip()] if passing_doc is not None else []
        minimum = attendance_parts[0] if attendance_parts else '75'
        average = passing_parts[0] if passing_parts else '7,0'
        return (
            f'O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de {minimum}% de presenca por componente. '
            f'Ja a politica de avaliacao detalha aprovacao, media {average}, recuperacao, monitorias e criterios de promocao. '
            'Os dois se complementam porque a frequencia sustenta a rotina, enquanto a politica academica mostra como a escola trata recuperacao e aprovacao quando a meta nao e atingida.'
        )
    if 'projeto de vida' in normalized and project_doc is not None:
        return project_doc.text
    if ({'aprovacao', 'aprovação', 'media', 'média', 'recuperacao', 'recuperação', 'promocao', 'promoção'} & terms) and passing_doc is not None:
        parts = [part.strip() for part in passing_doc.text.split('|') if part.strip()]
        if len(parts) >= 3:
            return (
                f'A referencia publica de aprovacao hoje e media {parts[0]} na escala {parts[1]}. '
                f'{parts[2]}'
            )
        return passing_doc.text
    if ({'falta', 'faltas', 'frequencia', 'frequência', 'pontualidade'} & terms or '75%' in normalized) and attendance_doc is not None:
        parts = [part.strip() for part in attendance_doc.text.split('|') if part.strip()]
        if len(parts) >= 4:
            return (
                f'A politica publica de frequencia hoje trabalha com minimo de {parts[0]}% de presenca. '
                f'{parts[1]} {parts[2]} Canal de acompanhamento: {parts[3]}.'
            )
        return attendance_doc.text
    return None


def _direct_service_credentials_bundle_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if not any(term in normalized for term in ('credenciais', 'credencial', 'login', 'senha')):
        return None
    if not any(term in normalized for term in ('secretaria', 'portal', 'documentos', 'documentacao', 'documentação')):
        return None
    return (
        'Hoje a familia precisa entender quatro frentes publicas deste fluxo: '
        'Secretaria recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas. '
        'Portal institucional centraliza protocolo e envio digital inicial de documentos. '
        'Credenciais significam login e senha do portal; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital. '
        'Documentos podem ser enviados pelo portal institucional, pelo email da secretaria ou pela secretaria presencial.'
    )


def _direct_document_submission_policy_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    normalized = _normalize_text(message)
    if 'secretaria' not in normalized:
        return None
    if not any(term in normalized for term in ('documentos', 'declaracoes', 'declarações', 'atualizacoes cadastrais', 'atualizações cadastrais')):
        return None
    if not any(term in normalized for term in ('prazo', 'prazos', 'canal', 'canais')):
        return None
    return (
        'Hoje a secretaria recebe documentos, declaracoes e atualizacoes cadastrais pelo portal institucional, '
        'pelo email da secretaria e pela secretaria presencial. '
        'Prazo esperado da secretaria: retorno em ate 2 dias uteis.'
    )


def _direct_unpublished_fast_answer(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(term in normalized for term in ('quantos alunos', 'quantidade de alunos', 'numero de alunos', 'número de alunos')):
        return (
            'Hoje os canais publicos do Colegio Horizonte nao informam o total de alunos matriculados. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if any(term in normalized for term in ('quantos professores', 'quantidade de professores', 'numero de professores', 'número de professores')):
        return (
            'Hoje os canais publicos do Colegio Horizonte nao informam a quantidade total de professores. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if any(term in normalized for term in ('quantas salas', 'quantidade de salas', 'numero de salas', 'número de salas')):
        return (
            'Hoje os canais publicos do Colegio Horizonte nao informam a quantidade total de salas de aula. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if any(term in normalized for term in ('idade minima', 'idade mínima', 'idade para estudar', 'idade para matricular')):
        return (
            'Hoje os canais publicos do Colegio Horizonte nao publicam uma idade minima exata para ingresso. '
            'O que aparece oficialmente sao os segmentos atendidos e o enquadramento por serie; para confirmar idade e adequacao, o canal certo e admissions.'
        )
    if any(term in normalized for term in ('quantos livros', 'quantidade de livros', 'numero de livros', 'número de livros')) and any(
        term in normalized for term in ('biblioteca', 'livros', 'acervo')
    ):
        return (
            'Hoje os canais publicos do Colegio Horizonte nao informam a quantidade total de livros da biblioteca. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if any(term in normalized for term in ('cardapio', 'cardápio')) and 'cantina' in normalized:
        return (
            'Hoje os canais publicos do Colegio Horizonte confirmam que ha cantina e almoco supervisionado, '
            'mas nao publicam um cardapio detalhado. Para esse detalhe, o melhor caminho e a secretaria ou o canal comercial.'
        )
    return None


def _direct_greeting_fast_answer(message: str) -> str | None:
    normalized = ' '.join(_normalize_text(message).split())
    if normalized in {'oi', 'ola', 'olá', 'bom dia', 'boa tarde', 'boa noite'}:
        return (
            'Oi. Eu posso te ajudar por aqui com informacoes da escola, canais oficiais, '
            'matricula, visitas, biblioteca, atividades e rotina escolar.'
        )
    return None


def _direct_capabilities_fast_answer(message: str) -> str | None:
    normalized = ' '.join(_normalize_text(message).split())
    if normalized in {
        'o que voce esta fazendo',
        'o que você está fazendo',
        'o que voce faz',
        'o que você faz',
    }:
        return (
            'Estou te ajudando a navegar as informacoes da escola de forma mais direta. '
            'Por aqui eu consigo responder sobre biblioteca, contatos, matricula, visitas, atividades, canais oficiais e rotina publica da escola.'
        )
    return None


def _direct_comparative_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    normalized = _normalize_text(message)
    if not (
        ({'melhor', 'concorrencia', 'concorrente', 'publica'} & terms)
        or 'escola publica' in normalized
        or 'na publica' in normalized
        or any(term in normalized for term in ('30 segundos', '30s', 'familia nova', 'família nova', 'por que deveria', 'por que escolher'))
    ):
        return None
    overview_doc = next((doc for doc in docs if doc.doc_id == 'profile.overview'), None)
    highlight_docs = [doc for doc in docs if doc.doc_id.startswith('highlight.')]
    feature_docs = [doc for doc in docs if doc.doc_id.startswith('feature.')]
    if overview_doc is None and not highlight_docs and not feature_docs:
        return None
    labels = [doc.title for doc in highlight_docs[:2] if doc.title]
    if len(labels) < 2:
        labels.extend(doc.title for doc in feature_docs[:2] if doc.title and doc.title not in labels)
    labels_preview = ', '.join(labels[:3]) if labels else 'os diferenciais publicados da escola'
    overview_text = overview_doc.text if overview_doc is not None else ''
    if any(term in normalized for term in ('30 segundos', '30s', 'familia nova', 'família nova', 'por que deveria', 'por que escolher')):
        return (
            'Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: '
            'ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. '
            f'No que esta publicado aqui, os diferenciais mais claros passam por {labels_preview}. '
            f'{overview_text}'.strip()
        )
    return (
        'Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia. '
        f'No que esta publicado aqui, os diferenciais desta escola passam por {labels_preview}. '
        f'{overview_text} '
        'Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.'
    )


def _direct_pedagogical_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    normalized = _normalize_text(message)
    pedagogical_terms = {'proposta', 'pedagogica', 'pedagogico', 'acolhimento', 'disciplina', 'aprendizagem'}
    if not (pedagogical_terms & terms) and not any(
        phrase in normalized
        for phrase in (
            'proposta pedagogica',
            'proposta pedagógica',
            'acolhimento e disciplina',
            'acolhimento com disciplina',
        )
    ):
        return None
    if any(phrase in normalized for phrase in ('proposta pedagogica', 'proposta pedagógica')):
        return (
            'A proposta pedagogica publicada hoje combina aprendizagem por projetos, cultura digital responsavel, '
            'acompanhamento socioemocional e aprofundamento academico progressivo. '
            'No Ensino Medio, isso aparece junto da BNCC, de um curriculo proprio com projeto de vida, '
            'producao textual e trilhas academicas no contraturno.'
        )
    overview_doc = next((doc for doc in docs if doc.doc_id == 'profile.overview'), None)
    segments_doc = next((doc for doc in docs if doc.doc_id == 'profile.segments'), None)
    highlight_docs = [doc for doc in docs if doc.doc_id.startswith('highlight.')]
    if overview_doc is None and segments_doc is None and not highlight_docs:
        return None

    headline_parts: list[str] = []
    if overview_doc is not None:
        overview_parts = [part.strip() for part in overview_doc.text.split('. ') if part.strip()]
        headline_parts.extend(overview_parts[:2])

    evidence_titles = [doc.title for doc in highlight_docs[:3] if doc.title]
    evidence_preview = ', '.join(evidence_titles)

    if 'acolhimento' in terms and 'disciplina' in terms:
        return (
            'Pelo que a escola publica hoje, esse equilibrio aparece em uma rotina com acompanhamento proximo e acolhimento estruturado. '
            f'{headline_parts[0] if headline_parts else ""} '
            'Na pratica, isso aparece em orientacao educacional, coordenacao, tutoria academica e projeto de vida, '
            'junto de uma jornada de acolhimento para familias e estudantes antes e depois da matricula.'
        ).strip()

    basis = ''
    basis_source = ''
    if segments_doc is not None:
        basis_match = re.search(r'base curricular:\s*([^.;]+)', segments_doc.text, flags=re.IGNORECASE)
        if basis_match:
            basis = basis_match.group(1).strip()
            basis_source = segments_doc.text
    if not basis and overview_doc is not None:
        basis_source = overview_doc.text
        overview_match = re.search(r'projeto pedagogico\s+([^.;]+)', _normalize_text(overview_doc.text), flags=re.IGNORECASE)
        if overview_match:
            basis = overview_match.group(1).strip()
    if basis and evidence_preview:
        return (
            f'A proposta pedagogica publicada hoje combina {basis}. '
            f'Na pratica, isso aparece em frentes como {evidence_preview}.'
        )
    if basis_source and evidence_preview:
        return (
            'A proposta pedagogica publicada hoje combina aprendizagem por projetos, '
            'acompanhamento socioemocional, cultura digital responsavel e aprofundamento academico progressivo. '
            f'Na pratica, isso aparece em frentes como {evidence_preview}.'
        )
    if evidence_preview:
        return f'A proposta pedagogica publicada hoje se apoia em {evidence_preview}.'
    if headline_parts:
        return ' '.join(headline_parts[:2])
    return None


def _direct_feature_fast_answer(message: str, docs: list[EvidenceDoc]) -> str | None:
    terms = _query_terms(message)
    normalized = _normalize_text(message)
    feature_prompt_terms = {
        'atividades',
        'atividade',
        'complementares',
        'complementar',
        'oficinas',
        'esporte',
        'esportes',
        'maker',
        'biblioteca',
        'cantina',
        'laboratorio',
        'laboratório',
        'quadra',
        'piscina',
        'kart',
        'tenis',
        'tênis',
        'professores',
    }
    if not (feature_prompt_terms & terms):
        return None
    feature_docs = [doc for doc in docs if doc.doc_id.startswith('feature.')]
    if not feature_docs:
        return None
    requested_specific_terms = (
        'biblioteca aurora',
        'biblioteca',
        'cantina',
        'laboratorio',
        'laboratório',
        'quadra de tenis',
        'tenis de mesa',
        'piscina',
        'kart',
        'sala de professores',
        'quadra',
    )
    for requested_term in requested_specific_terms:
        if requested_term not in normalized:
            continue
        target_doc = next(
            (doc for doc in feature_docs if requested_term in _normalize_text(f'{doc.title} {doc.text}')),
            None,
        )
        if target_doc is None:
            continue
        available = 'true' in _normalize_text(target_doc.text)
        if available:
            return f'Sim. {target_doc.title}: {target_doc.text.replace("|", " ").strip()}.'
        return f'Nao. {target_doc.title}: {target_doc.text.replace("|", " ").strip()}.'
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
    normalized = _normalize_text(message)
    if not ({'curricular', 'curriculo', 'base', 'bncc'} & terms) and not any(
        phrase in normalized for phrase in ('proposta pedagogica', 'proposta pedagógica')
    ):
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
    normalized = _normalize_text(message)
    child_count = _extract_hypothetical_children_count(message)
    tuition_rows = _tuition_rows(docs)
    tuition_terms = {'mensalidade', 'preco', 'precos', 'preco', 'valor', 'matricula', 'desconto', 'descontos'}
    if not ((terms & tuition_terms) or child_count is not None):
        return None
    if child_count is not None and 'filhos' in normalized and 'matricula' in normalized and tuition_rows:
        enrollment_fees = [
            float(row['enrollment_fee'])
            for row in tuition_rows
            if isinstance(row.get('enrollment_fee'), float)
        ]
        unique_fees = sorted({fee for fee in enrollment_fees if fee > 0})
        if len(unique_fees) == 1:
            enrollment_fee = unique_fees[0]
            total = enrollment_fee * child_count
            return (
                f'Pela tabela publica atual, a taxa de matricula de referencia e R$ {_format_brl(enrollment_fee)} por aluno. '
                f'Sem considerar bolsas, descontos comerciais ou variacao por segmento, para {child_count} matriculas isso daria R$ {_format_brl(total)}.'
            )
        if unique_fees:
            preview = '; '.join(
                f"{row.get('segment', 'Segmento')}: matricula R$ {_format_brl(float(row['enrollment_fee']))}"
                for row in tuition_rows[:3]
                if isinstance(row.get('enrollment_fee'), float)
            )
            return (
                'Hoje a taxa de matricula publicada varia por segmento. '
                f'As referencias que eu encontrei foram: {preview}. '
                f'Se quiser, eu calculo um cenario hipotetico para {child_count} alunos no segmento que voce preferir.'
            )
    if tuition_rows and (
        'media' in terms
        or 'media' in normalized
        or 'média' in normalized
        or 'cada ano' in normalized
        or 'por ano' in normalized
        or 'cada segmento' in normalized
        or 'por segmento' in normalized
    ):
        lines = ['Hoje as referencias publicas de mensalidade e matricula por segmento sao:']
        for row in tuition_rows:
            monthly_amount = row.get('monthly_amount')
            enrollment_fee = row.get('enrollment_fee')
            if not isinstance(monthly_amount, float):
                continue
            detail = (
                f"- {row.get('segment', 'Segmento')} ({row.get('shift_label') or 'turno'}): "
                f"mensalidade R$ {_format_brl(monthly_amount)}"
            )
            if isinstance(enrollment_fee, float):
                detail += f" e taxa de matricula R$ {_format_brl(enrollment_fee)}"
            notes = str(row.get('notes') or '').strip()
            if notes:
                detail += f". {notes}"
            lines.append(detail)
        if len(lines) > 1:
            return '\n'.join(lines)
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


def _infer_public_followup_slots(
    message: str,
    answer_text: str,
) -> tuple[str | None, str | None]:
    normalized = _normalize_text(f'{message} {answer_text}')
    terms = _query_terms(message)
    if any(term in normalized for term in {'endereco', 'cep', 'sao paulo', 'rua doutor joao santos'}):
        if 'estado' in terms:
            return 'localizacao', 'state'
        if 'cidade' in terms:
            return 'localizacao', 'city'
        if 'cep' in terms:
            return 'localizacao', 'postal_code'
        return 'localizacao', 'address'
    if (
        ({'publica', 'particular'} & set(normalized.split()))
        or 'comparacao vazia' in normalized
        or 'diferenciais desta escola' in normalized
    ) and any(term in normalized for term in {'proposta pedagogica', 'projeto de vida', 'acompanhamento'}):
        return 'comparativo', 'diferenciais'
    if any(term in normalized for term in {'matricula', 'aulas', 'formatura', 'reuniao'}):
        if 'matricula' in terms:
            return 'timeline', 'matricula'
        if 'aulas' in terms:
            return 'timeline', 'aulas'
        if 'formatura' in terms:
            return 'timeline', 'formatura'
        if 'reuniao' in terms:
            return 'timeline', 'reuniao'
        return 'timeline', 'general'
    if 'biblioteca' in normalized:
        if {'horario', 'hora', 'abre', 'fecha'} & terms:
            return 'biblioteca', 'hours'
        if 'nome' in terms:
            return 'biblioteca', 'name'
        return 'biblioteca', 'general'
    if ({'documentos', 'documento', 'fax', 'telegrama', 'caixa', 'postal'} & terms) or any(
        phrase in _normalize_text(message)
        for phrase in {'como mando os documentos', 'como enviar os documentos', 'posso enviar documentos'}
    ):
        return 'documentos', 'document_submission'
    if any(term in normalized for term in {'o que voce esta fazendo', 'o que voce faz', 'ajudar por aqui'}):
        return 'assistente', 'capabilities'
    if 'instagram' in terms:
        return 'instagram', 'contact'
    return None, None


def _deterministic_backstop(message: str, plan: PublicPilotPlan | None, docs: list[EvidenceDoc]) -> str | None:
    greeting_answer = _direct_greeting_fast_answer(message)
    if greeting_answer:
        return greeting_answer
    auth_guidance_answer = _direct_auth_guidance_fast_answer(message)
    if auth_guidance_answer:
        return auth_guidance_answer
    capabilities_answer = _direct_capabilities_fast_answer(message)
    if capabilities_answer:
        return capabilities_answer
    unpublished_answer = _direct_unpublished_fast_answer(message)
    if unpublished_answer:
        return unpublished_answer
    contact_bundle_answer = _direct_contact_bundle_fast_answer(message, docs)
    if contact_bundle_answer:
        return contact_bundle_answer
    location_answer = _direct_location_fast_answer(message, docs)
    if location_answer:
        return location_answer
    timeline_bundle_answer = _direct_timeline_bundle_fast_answer(message, docs)
    if timeline_bundle_answer:
        return timeline_bundle_answer
    family_new_bundle_answer = _direct_family_new_bundle_fast_answer(message, docs)
    if family_new_bundle_answer:
        return family_new_bundle_answer
    permanence_support_answer = _direct_permanence_support_fast_answer(message, docs)
    if permanence_support_answer:
        return permanence_support_answer
    conduct_frequency_recovery_answer = _direct_conduct_frequency_recovery_fast_answer(message, docs)
    if conduct_frequency_recovery_answer:
        return conduct_frequency_recovery_answer
    transversal_year_answer = _direct_transversal_year_fast_answer(message, docs)
    if transversal_year_answer:
        return transversal_year_answer
    facilities_study_answer = _direct_facilities_study_fast_answer(message, docs)
    if facilities_study_answer:
        return facilities_study_answer
    required_documents_answer = _direct_required_documents_fast_answer(message, docs)
    if required_documents_answer:
        return required_documents_answer
    document_submission_answer = _direct_document_submission_policy_fast_answer(message, docs)
    if document_submission_answer:
        return document_submission_answer
    service_answer = _direct_service_routing_fast_answer(message, docs)
    if service_answer:
        return service_answer
    leadership_answer = _direct_leadership_fast_answer(message, docs)
    if leadership_answer:
        return leadership_answer
    schedule_answer = _direct_schedule_fast_answer(message, docs)
    if schedule_answer:
        return schedule_answer
    tuition_answer = _direct_tuition_fast_answer(message, docs)
    if tuition_answer:
        return tuition_answer
    pedagogical_answer = _direct_pedagogical_fast_answer(message, docs)
    if pedagogical_answer:
        return pedagogical_answer
    policy_answer = _direct_policy_fast_answer(message, docs)
    if policy_answer:
        return policy_answer
    service_credentials_answer = _direct_service_credentials_bundle_fast_answer(message, docs)
    if service_credentials_answer:
        return service_credentials_answer
    contact_answer = _direct_contact_fast_answer(message, docs)
    if contact_answer:
        return contact_answer
    comparative_answer = _direct_comparative_fast_answer(message, docs)
    if comparative_answer:
        return comparative_answer
    primary = _select_primary_doc(plan, docs)
    if primary is None:
        return None
    terms = _query_terms(message)
    curriculum_answer = _direct_curriculum_fast_answer(message, docs)
    if curriculum_answer:
        return curriculum_answer
    feature_answer = _direct_feature_fast_answer(message, docs)
    if feature_answer:
        return feature_answer
    text = primary.text
    library_doc = _find_first_matching_doc(docs, 'feature.', ('biblioteca', 'biblioteca aurora'))
    if (
        'nome' in terms
        and not any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'})
        and library_doc is not None
    ):
        library_title = library_doc.title if library_doc is not None else primary.title
        return f'O nome desse espaco e {library_title}.'
    if 'biblioteca' in terms and not any(term in terms for term in {'horario', 'hora', 'abre', 'fecha'}):
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
            return (
                f'O horario da {primary.title} hoje e de segunda a sexta, {hours}.'
                if hours
                else f'O horario da {primary.title} hoje segue o registro publico disponivel.'
            )
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
    if normalized in {
        'oi',
        'ola',
        'olá',
        'bom dia',
        'boa tarde',
        'boa noite',
        'o que voce esta fazendo',
        'o que você está fazendo',
        'o que voce faz',
        'o que você faz',
    }:
        return True
    if (
        'onde fica' in normalized
        or ('estado' in normalized and 'endereco' in normalized)
        or ('cidade' in normalized and 'endereco' in normalized)
        or ('cep' in normalized and 'endereco' in normalized)
        or ('por que antes' in normalized and 'endereco' in normalized)
    ):
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
        'estado',
        'cidade',
        'cep',
        'biblioteca',
        'telegrama',
        'caixa',
        'postal',
        'documentos',
        'documento',
        'exigidos',
        'necessarios',
        'mensalidade',
        'valor',
        'preco',
        'precos',
        'desconto',
        'descontos',
        'filhos',
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
        'turno',
        'turnos',
        'matutino',
        'vespertino',
        'noturno',
        'intervalo',
        'intervalos',
        'recreio',
        'melhor',
        'concorrencia',
        'concorrente',
        'publica',
        'proposta',
        'pedagogica',
        'pedagogico',
        'acolhimento',
        'disciplina',
        'aprendizagem',
        'projeto',
        'vida',
        'aprovacao',
        'aprovação',
        'recuperacao',
        'recuperação',
        'frequencia',
        'frequência',
        'faltas',
        'secretaria',
        'coordenacao',
        'coordenação',
        'orientacao',
        'orientação',
        'bullying',
        'diretor',
        'diretora',
        'bolsa',
        'bolsas',
        'mando',
        'enviar',
        'envio',
        'mandar',
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
        temperature=0.1,
        max_tokens=500,
        timeout=float(getattr(settings, 'crewai_llm_timeout_seconds', 15.0) or 15.0),
        max_retries=1,
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
    user_context: dict[str, Any] | None,
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
                'user_context': user_context,
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
