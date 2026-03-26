from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any
import unicodedata


@dataclass(frozen=True)
class PublicEvidenceFact:
    key: str
    text: str


@dataclass(frozen=True)
class PublicEvidenceBundle:
    primary_act: str
    secondary_acts: tuple[str, ...]
    facts: tuple[PublicEvidenceFact, ...]


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize('NFKD', text)
    without_accents = ''.join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.replace('º', 'o').replace('ª', 'a').lower()


def _message_matches_term(message: str, term: str) -> bool:
    normalized_term = _normalize_text(term).strip()
    if not normalized_term:
        return False
    pattern = r'(?<!\w)' + r'\s+'.join(re.escape(part) for part in normalized_term.split()) + r'(?!\w)'
    return re.search(pattern, message) is not None


def _as_list_of_dicts(profile: dict[str, Any], key: str) -> list[dict[str, Any]]:
    entries = profile.get(key)
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _segments_text(profile: dict[str, Any]) -> str | None:
    segments = [str(item).strip() for item in profile.get('segments', []) if isinstance(item, str) and str(item).strip()]
    if not segments:
        return None
    return 'Segmentos publicos atendidos: ' + '; '.join(segments) + '.'


def _tuition_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'tuition_reference')
    facts: list[str] = []
    for row in rows[:3]:
        facts.append(
            '{segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                shift_label=row.get('shift_label', 'turno'),
                monthly_amount=row.get('monthly_amount', '0.00'),
                enrollment_fee=row.get('enrollment_fee', '0.00'),
                notes=str(row.get('notes', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _shift_offer_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'shift_offers')
    facts: list[str] = []
    for row in rows[:3]:
        facts.append(
            '{segment}: {starts_at} as {ends_at}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                starts_at=row.get('starts_at', '--:--'),
                ends_at=row.get('ends_at', '--:--'),
                notes=str(row.get('notes', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _feature_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'feature_inventory')
    facts: list[str] = []
    for row in rows[:8]:
        availability = 'disponivel' if bool(row.get('available')) else 'nao disponivel'
        facts.append(
            '{label}: {availability}. {notes}'.format(
                label=row.get('label', row.get('feature_key', 'Recurso')),
                availability=availability,
                notes=str(row.get('notes', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _contact_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'contact_channels')
    facts: list[str] = []
    for row in rows[:8]:
        facts.append(
            '{label} ({channel}): {value}'.format(
                label=row.get('label', 'Contato'),
                channel=row.get('channel', 'canal'),
                value=row.get('value', 'nao informado'),
            ).strip()
        )
    return [text for text in facts if text]


def _leadership_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'leadership_team')
    facts: list[str] = []
    for row in rows[:4]:
        facts.append(
            '{title}: {name}. {focus} Contato: {contact}. {notes}'.format(
                title=row.get('title', 'Lideranca'),
                name=row.get('name', 'nao informado'),
                focus=str(row.get('focus', '')).strip(),
                contact=row.get('contact_channel', 'nao informado'),
                notes=str(row.get('notes', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _highlight_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'highlights')
    facts: list[str] = []
    for row in rows[:4]:
        facts.append(
            '{title}: {description}. Evidencia: {evidence}'.format(
                title=row.get('title', 'Diferencial'),
                description=str(row.get('description', '')).strip(),
                evidence=str(row.get('evidence_line', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _service_texts(profile: dict[str, Any]) -> list[str]:
    rows = _as_list_of_dicts(profile, 'service_catalog')
    facts: list[str] = []
    for row in rows[:6]:
        facts.append(
            '{title}: publico {audience}; canal {request_channel}; prazo {typical_eta}. {notes}'.format(
                title=row.get('title', 'Servico'),
                audience=row.get('audience', 'nao informado'),
                request_channel=row.get('request_channel', 'nao informado'),
                typical_eta=row.get('typical_eta', 'nao informado'),
                notes=str(row.get('notes', '')).strip(),
            ).strip()
        )
    return [text for text in facts if text]


def _curriculum_text(profile: dict[str, Any]) -> str | None:
    basis = str(profile.get('curriculum_basis', '')).strip()
    components = [str(item).strip() for item in profile.get('curriculum_components', []) if isinstance(item, str) and str(item).strip()]
    if basis and components:
        return basis + ' Componentes publicados: ' + ', '.join(components[:12]) + '.'
    if basis:
        return basis
    return None


def _location_text(profile: dict[str, Any]) -> str | None:
    address = str(profile.get('address_line', '')).strip()
    district = str(profile.get('district', '')).strip()
    city = str(profile.get('city', '')).strip()
    state = str(profile.get('state', '')).strip()
    postal_code = str(profile.get('postal_code', '')).strip()
    parts = [part for part in [address, district, city, state, postal_code] if part]
    if not parts:
        return None
    return 'Endereco publico: ' + ', '.join(parts) + '.'


def _timeline_texts(
    profile: dict[str, Any],
    *,
    request_message: str,
    focus_hint: str | None,
) -> list[str]:
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return []
    normalized = _normalize_text(' '.join(part for part in [focus_hint or '', request_message] if part).strip())

    chosen: dict[str, Any] | None = None
    if any(_message_matches_term(normalized, term) for term in {'matricula', 'matrícula'}):
        chosen = next(
            (
                item
                for item in entries
                if isinstance(item, dict) and 'admissions_opening' in str(item.get('topic_key', ''))
            ),
            None,
        )
    elif any(_message_matches_term(normalized, term) for term in {'formatura', 'graduacao', 'graduação'}):
        chosen = next(
            (
                item
                for item in entries
                if isinstance(item, dict) and 'graduation' in str(item.get('topic_key', ''))
            ),
            None,
        )
    elif any(
        _message_matches_term(normalized, term)
        for term in {'inicio das aulas', 'início das aulas', 'comecam as aulas', 'começam as aulas', 'ano letivo'}
    ):
        chosen = next(
            (
                item
                for item in entries
                if isinstance(item, dict) and 'school_year_start' in str(item.get('topic_key', ''))
            ),
            None,
        )

    if chosen is None:
        chosen = next((item for item in entries if isinstance(item, dict)), None)
    if not isinstance(chosen, dict):
        return []

    title = str(chosen.get('title', '')).strip()
    summary = str(chosen.get('summary', '')).strip()
    notes = str(chosen.get('notes', '')).strip()
    text = ' '.join(part for part in [title + ':' if title else '', summary, notes] if part).strip()
    return [text] if text else []


def _calendar_event_texts(
    profile: dict[str, Any],
    *,
    request_message: str,
    focus_hint: str | None,
) -> list[str]:
    events = profile.get('public_calendar_events')
    if not isinstance(events, list):
        return []
    normalized = _normalize_text(' '.join(part for part in [focus_hint or '', request_message] if part).strip())
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', normalized)
        if token not in {
            'quando',
            'qual',
            'quais',
            'que',
            'dia',
            'data',
            'evento',
            'eventos',
            'publico',
            'publicos',
            'escola',
            'colegio',
        }
    }
    scored: list[tuple[int, dict[str, Any]]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        haystack = _normalize_text(
            ' '.join(
                str(event.get(key, '')).strip()
                for key in ('title', 'description', 'category', 'audience')
            )
        )
        score = sum(2 for token in tokens if token in haystack)
        if score > 0:
            scored.append((score, event))
    if scored:
        scored.sort(key=lambda item: (-item[0], str(item[1].get('starts_at', '')), str(item[1].get('title', ''))))
        selected = [event for _score, event in scored[:2]]
    else:
        selected = [event for event in events[:2] if isinstance(event, dict)]

    facts: list[str] = []
    for event in selected:
        title = str(event.get('title', 'Evento publico')).strip()
        description = str(event.get('description', '')).strip()
        starts_at = str(event.get('starts_at', '')).strip()
        text = ' '.join(part for part in [title + ':', starts_at, description] if part).strip()
        if text:
            facts.append(text)
    return facts


def build_public_evidence_bundle(
    profile: dict[str, Any],
    *,
    primary_act: str,
    secondary_acts: tuple[str, ...] = (),
    request_message: str = '',
    focus_hint: str | None = None,
) -> PublicEvidenceBundle | None:
    school_name = str(profile.get('school_name', 'Colegio Horizonte')).strip() or 'Colegio Horizonte'
    facts: list[PublicEvidenceFact] = [
        PublicEvidenceFact('school_name', f'Nome oficial da escola: {school_name}.'),
    ]
    seen = {('school_name', facts[0].text)}

    def add(key: str, text: str | None) -> None:
        cleaned = str(text or '').strip()
        if not cleaned:
            return
        signature = (key, cleaned)
        if signature in seen:
            return
        seen.add(signature)
        facts.append(PublicEvidenceFact(key, cleaned))

    def add_many(key: str, values: list[str]) -> None:
        for value in values:
            add(key, value)

    acts = [primary_act, *secondary_acts[:2]]
    for act in acts:
        if act in {'canonical_fact', 'school_name'}:
            add('segments', _segments_text(profile))
            add_many('highlights', _highlight_texts(profile)[:2])
        if act in {'segments'}:
            add('segments', _segments_text(profile))
        if act in {'pricing'}:
            add_many('tuition_reference', _tuition_texts(profile))
            add_many('service_catalog', _service_texts(profile)[:2])
        if act in {'features', 'schedule', 'operating_hours'}:
            add_many('shift_offers', _shift_offer_texts(profile))
            add_many('feature_inventory', _feature_texts(profile)[:6])
        if act in {'contacts', 'web_presence', 'social_presence'}:
            add_many('contact_channels', _contact_texts(profile))
        if act in {'leadership'}:
            add_many('leadership_team', _leadership_texts(profile))
        if act in {'careers'}:
            add_many('service_catalog', _service_texts(profile))
            add_many('contact_channels', _contact_texts(profile))
        if act in {'curriculum'}:
            add('curriculum_basis', _curriculum_text(profile))
            add_many('shift_offers', _shift_offer_texts(profile)[:2])
        if act in {'highlight', 'comparative'}:
            add_many('highlights', _highlight_texts(profile))
        if act in {'visit'}:
            add_many('service_catalog', _service_texts(profile)[:2])
        if act in {'location'}:
            add('location', _location_text(profile))
        if act in {'confessional'}:
            confessional_status = str(profile.get('confessional_status', '')).strip()
            if confessional_status:
                add('confessional_status', f'Carater confessional publicado: {confessional_status}.')
        if act in {'timeline'}:
            add_many('public_timeline', _timeline_texts(profile, request_message=request_message, focus_hint=focus_hint))
        if act in {'calendar_events'}:
            add_many(
                'public_calendar_events',
                _calendar_event_texts(profile, request_message=request_message, focus_hint=focus_hint),
            )

    if len(facts) <= 1:
        return None
    return PublicEvidenceBundle(
        primary_act=primary_act,
        secondary_acts=tuple(secondary_acts[:2]),
        facts=tuple(facts),
    )
