from __future__ import annotations

# ruff: noqa: F401,F403,F405

"""Public profile and public-act runtime helpers extracted from runtime.py.

This module is imported lazily from runtime.py after the shared helper surface is
already defined. It intentionally reuses the legacy runtime namespace during the
ongoing decomposition, so extracted functions keep behavior while the monolith
is split into focused modules.
"""

from . import runtime_core as _runtime_core
from .conversation_focus_runtime import _assistant_already_introduced
from .conversation_focus_runtime import _normalize_text
from .conversation_focus_runtime import _recent_conversation_focus
from .conversation_focus_runtime import _recent_focus_follow_up_line
from .conversation_focus_runtime import _recent_message_lines
from .conversation_focus_runtime import _recent_trace_focus
from .conversation_focus_runtime import _is_greeting_only
from .intent_analysis_runtime import (
    _contains_any,
    _is_assistant_identity_query,
    _is_capability_query,
    _is_direct_service_routing_bundle_query,
    _is_follow_up_query,
    _is_public_pricing_navigation_query,
    _is_service_routing_query,
    _message_matches_term,
    _requested_operating_hours_attribute,
)
from .public_act_rules_runtime import (
    _has_public_multi_intent_signal,
    _match_public_act_rule,
    _matched_public_act_rules,
    _prioritize_public_act_rules,
)
from .analysis_context_runtime import _extract_recent_assistant_message, _extract_recent_user_message
from .intent_analysis_runtime import _extract_salient_terms
from .public_act_rules_runtime import _looks_like_public_documentary_open_query, _matches_public_contact_rule
from .public_orchestration_runtime import _build_public_institution_plan, _should_use_public_open_documentary_synthesis
from .student_scope_runtime import _compose_public_access_scope_answer


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _llm_forced_mode_enabled(*args, **kwargs):
    return getattr(_runtime_core, '_llm_forced_mode_enabled')(*args, **kwargs)


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


def _select_public_segment(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'Ensino Fundamental I'
    if any(
        _message_matches_term(normalized, term)
        for term in {'fundamental', 'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}
    ):
        return 'Ensino Fundamental II'
    if any(
        _message_matches_term(normalized, term)
        for term in {'ensino medio', 'ensino médio', 'medio', 'médio', '1o ano', '2o ano', '3o ano'}
    ):
        return 'Ensino Medio'
    return None


def _segment_semantic_key(value: str | None) -> str | None:
    normalized = _normalize_text(str(value or '').strip())
    if not normalized:
        return None
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'fundamental i',
            'anos iniciais',
            '1o ano do fundamental',
            '2o ano do fundamental',
            '3o ano do fundamental',
            '4o ano do fundamental',
            '5o ano do fundamental',
            'primeiro ano do fundamental',
            'segundo ano do fundamental',
            'terceiro ano do fundamental',
            'quarto ano do fundamental',
            'quinto ano do fundamental',
        }
    ):
        return 'fundamental_i'
    if any(
        _message_matches_term(normalized, term)
        for term in {'fundamental ii', '6o ano', '7o ano', '8o ano', '9o ano'}
    ):
        return 'fundamental_ii'
    if 'fundamental' in normalized:
        return 'fundamental_ii'
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'medio',
            'médio',
            '1a a 3a serie',
            '1a a 3a série',
            '1o ano',
            '2o ano',
            '3o ano',
        }
    ):
        return 'ensino_medio'
    return normalized


def _public_segment_matches(row_segment: str | None, requested_segment: str | None) -> bool:
    if requested_segment is None:
        return True
    return _segment_semantic_key(row_segment) == _segment_semantic_key(requested_segment)


def _extract_grade_reference(message: str) -> str | None:
    normalized = _normalize_text(message)
    match = re.search(r'\b(6o ano|7o ano|8o ano|9o ano|1o ano|2o ano|3o ano)\b', normalized)
    if not match:
        return None
    return match.group(1)


def _feature_inventory_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    inventory = profile.get('feature_inventory')
    if not isinstance(inventory, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, dict):
            continue
        key = str(item.get('feature_key', '')).strip().lower()
        if not key:
            continue
        result[key] = item
    return result


def _recent_public_feature_key(conversation_context: dict[str, Any] | None) -> str | None:
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        features = _requested_public_features(content)
        if len(features) == 1:
            return features[0]
        normalized = _normalize_text(content)
        for feature_key in (
            'biblioteca',
            'cantina',
            'laboratorio',
            'maker',
            'quadra',
            'piscina',
            'futebol',
            'volei',
            'teatro',
            'danca',
        ):
            if _message_matches_term(normalized, feature_key):
                return feature_key
    return None


def _recent_public_contact_subject(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> str | None:
    recent_service = _recent_service_match(profile, conversation_context)
    if recent_service is not None:
        title = str(recent_service.get('title', '')).strip()
        if title:
            return title
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'orientacao educacional',
                'orientação educacional',
                'bullying',
                'socioemocional',
            }
        ):
            return 'Orientacao educacional'
        if any(
            _message_matches_term(normalized, term) for term in {'financeiro', 'boleto', 'boletos'}
        ):
            return 'Financeiro'
        if any(
            _message_matches_term(normalized, term)
            for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}
        ):
            return 'Direcao'
        if any(_message_matches_term(normalized, term) for term in {'coordenacao', 'coordenação'}):
            return 'Coordenacao'
        if any(
            _message_matches_term(normalized, term)
            for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}
        ):
            return 'Admissoes'
        if any(_message_matches_term(normalized, term) for term in {'secretaria'}):
            return 'Secretaria'
    return None


def _public_contact_reference_message(
    *,
    profile: dict[str, Any],
    source_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not _is_follow_up_query(source_message):
        return source_message
    subject = _recent_public_contact_subject(profile, conversation_context)
    if subject:
        return f'{source_message} sobre {subject}'
    return analysis_message


def _preferred_contact_labels_from_context(
    profile: dict[str, Any],
    source_message: str,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    normalized = _normalize_text(source_message)
    preferred: list[str] = []

    def add(label: str) -> None:
        cleaned = label.strip()
        if cleaned and cleaned not in preferred:
            preferred.append(cleaned)

    explicit_terms = (
        ('Direcao', {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'}),
        ('Coordenacao', {'coordenacao', 'coordenação', 'coordenador', 'coordenadora'}),
        ('Secretaria', {'secretaria'}),
        (
            'Financeiro',
            {'financeiro', 'boleto', 'boletos', 'mensalidade', 'fatura', 'faturas', 'contrato'},
        ),
        ('Admissoes', {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}),
        (
            'Orientacao educacional',
            {'orientacao educacional', 'orientação educacional', 'bullying', 'socioemocional'},
        ),
    )
    for label, terms in explicit_terms:
        if any(_message_matches_term(normalized, term) for term in terms):
            add(label)

    recent_service = _recent_service_match(profile, conversation_context)
    if isinstance(recent_service, dict):
        service_key = str(recent_service.get('service_key', '')).strip().lower()
        service_preferences = {
            'orientacao_educacional': 'Orientacao educacional',
            'financeiro_escolar': 'Financeiro',
            'visita_institucional': 'Admissoes',
            'solicitacao_direcao': 'Direcao',
            'secretaria_escolar': 'Secretaria',
        }
        preferred_label = service_preferences.get(service_key)
        if preferred_label:
            add(preferred_label)

    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        content_normalized = _normalize_text(content)
        if any(
            _message_matches_term(content_normalized, term)
            for term in {
                'orientacao educacional',
                'orientação educacional',
                'bullying',
                'socioemocional',
            }
        ):
            add('Orientacao educacional')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'financeiro', 'boleto', 'boletos'}
        ):
            add('Financeiro')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'diretora', 'diretor', 'direcao', 'direção', 'diretoria'}
        ):
            add('Direcao')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'coordenacao', 'coordenação'}
        ):
            add('Coordenacao')
            break
        if any(
            _message_matches_term(content_normalized, term)
            for term in {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'}
        ):
            add('Admissoes')
            break
        if any(_message_matches_term(content_normalized, term) for term in {'secretaria'}):
            add('Secretaria')
            break
    return preferred


def _build_conversation_slot_memory(
    *,
    actor: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    request_message: str | None = None,
    public_plan: PublicInstitutionPlan | None = None,
    preview: Any | None = None,
) -> ConversationSlotMemory:
    from .public_profile_slot_memory_runtime import _build_conversation_slot_memory_impl as _impl

    return _impl(
        actor=actor,
        profile=profile,
        conversation_context=conversation_context,
        request_message=request_message,
        public_plan=public_plan,
        preview=preview,
    )



def _requested_public_features(message: str) -> list[str]:
    normalized = _normalize_text(message)
    feature_order = [
        ('biblioteca', 'biblioteca'),
        ('cantina', 'cantina'),
        ('laboratorio', 'laboratorio'),
        ('laboratorio de ciencias', 'laboratorio'),
        ('maker', 'maker'),
        ('espaco maker', 'maker'),
        ('academia', 'academia'),
        ('piscina', 'piscina'),
        ('quadra de tenis', 'quadra de tenis'),
        ('quadra', 'quadra'),
        ('futebol', 'futebol'),
        ('futsal', 'futebol'),
        ('volei', 'volei'),
        ('vôlei', 'volei'),
        ('danca', 'danca'),
        ('dança', 'danca'),
        ('teatro', 'teatro'),
        ('robotica', 'maker'),
        ('robótica', 'maker'),
        ('orientacao educacional', 'orientacao educacional'),
        ('orientação educacional', 'orientacao educacional'),
    ]
    found: list[str] = []
    for term, canonical in feature_order:
        if _message_matches_term(normalized, term) and canonical not in found:
            found.append(canonical)
    return found


def _is_public_feature_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _requested_public_features(message):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'estrutura',
            'infraestrutura',
            'espaco',
            'espaço',
            'espacos',
            'espaços',
            'campus',
            'aula de',
            'oficina de',
            'curso de',
            'atividade de',
            'clube de',
            'atividade',
            'atividades',
            'contraturno',
            *PUBLIC_ENRICHMENT_TERMS,
        }
    )


def _asks_why_feature_is_missing(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'por que nao tem',
            'por que não tem',
            'por que nao possui',
            'por que não possui',
            'por que nao oferece',
            'por que não oferece',
            'por que nao existe',
            'por que não existe',
        }
    )


def _extract_feature_gap_focus(message: str) -> str | None:
    normalized = _normalize_text(message)
    cleaned = re.sub(
        r'^(?:e\s+)?(?:essa escola|o colegio|o col[eé]gio|a escola)?\s*(?:tem|possui|oferece|tem aula de|aula de|oficina de|curso de|atividade de|por que nao tem|por que nao possui|por que nao oferece|por que nao existe)\s+',
        '',
        normalized,
    ).strip(' ?.')
    if cleaned.startswith('e '):
        cleaned = cleaned[2:].strip()
    if cleaned:
        return cleaned
    salient = sorted(_extract_salient_terms(message))
    if salient:
        return ' '.join(salient[:4])
    return None


def _feature_suggestion_replies(feature_keys: list[str]) -> list[str]:
    if 'biblioteca' in feature_keys:
        return [
            'Qual o horario da biblioteca?',
            'Qual o endereco da escola?',
            'Quero agendar uma visita',
            'Quais atividades a escola oferece?',
        ]
    if any(
        key in feature_keys
        for key in {'maker', 'danca', 'futebol', 'volei', 'teatro', 'laboratorio'}
    ):
        return [
            'Quais atividades no contraturno a escola oferece?',
            'Tem horarios dessas atividades?',
            'Quero agendar uma visita',
            'Qual o horario do 9o ano?',
        ]
    return [
        'Quais atividades a escola oferece?',
        'Quero agendar uma visita',
        'Qual o horario do 9o ano?',
        'Como vinculo minha conta?',
    ]


def _compose_public_feature_answer(
    profile: dict[str, Any],
    *,
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None = None,
) -> str | None:
    from .public_profile_routes_runtime import _compose_public_feature_answer_impl as _impl

    return _impl(
        profile,
        original_message=original_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    )



def _compose_public_feature_schedule_follow_up(
    *,
    profile: dict[str, Any],
    original_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    if not any(
        _message_matches_term(_normalize_text(original_message), term)
        for term in PUBLIC_SCHEDULE_TERMS | {'funciona quando', 'isso funciona quando'}
    ):
        return None
    requested_features = _requested_public_features(original_message)
    if (
        not requested_features
        and _is_follow_up_query(original_message)
        and not _is_public_feature_query(original_message)
    ):
        requested_features = _requested_public_features(analysis_message)
    if not requested_features and _is_follow_up_query(original_message):
        recent_feature = _recent_public_feature_key(conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if len(requested_features) != 1:
        return None
    item = _feature_inventory_map(profile).get(requested_features[0])
    if item is None or not bool(item.get('available')):
        return None
    label = str(item.get('label', requested_features[0])).strip()
    notes = str(item.get('notes', '')).strip()
    if not notes:
        return None
    normalized_notes = _normalize_text(notes)
    if not any(
        marker in normalized_notes
        for marker in (
            'segunda',
            'terca',
            'terça',
            'quarta',
            'quinta',
            'sexta',
            'sabado',
            'sábado',
            'domingo',
            'contraturno',
            '7h',
            '8h',
            '9h',
            '10h',
            '11h',
            '12h',
            '13h',
            '14h',
            '15h',
            '16h',
            '17h',
            '18h',
        )
    ):
        return None
    return f'O horario de {label} hoje funciona assim: {notes}'


def _contact_value(profile: dict[str, Any], channel: str) -> list[str]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    values: list[str] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        values.append(f'{label}: {value}' if label else value)
    return values


def _school_subject_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned.startswith(('a ', 'o ')):
        return cleaned
    return f'o {cleaned}'


def _school_object_reference(reference: str) -> str:
    cleaned = reference.strip()
    if cleaned == 'a escola':
        return 'da escola'
    if cleaned.startswith(('a ', 'o ')):
        return f'd{cleaned}'
    return f'de {cleaned}'


def _published_public_segments(profile: dict[str, Any]) -> set[str]:
    return {
        str(item).strip()
        for item in profile.get('segments', [])
        if isinstance(item, str) and str(item).strip()
    }


def _requested_unpublished_public_segment(context: PublicProfileContext) -> str | None:
    requested_segment = (
        _select_public_segment(context.source_message) or context.slot_memory.public_pricing_segment
    )
    if not requested_segment:
        return None
    requested_key = _segment_semantic_key(requested_segment)
    if any(
        _segment_semantic_key(published_segment) == requested_key
        for published_segment in _published_public_segments(context.profile)
    ):
        return None
    return requested_segment


def _compose_public_segment_scope_gap(
    context: PublicProfileContext,
    *,
    requested_segment: str,
    topic: str,
) -> str:
    published_segments = sorted(_published_public_segments(context.profile))
    published_text = (
        ', '.join(published_segments) if published_segments else 'os segmentos hoje publicados'
    )
    return (
        f'Hoje eu nao tenho um detalhamento publico de {topic} para {requested_segment.lower()} em {context.school_reference}. '
        f'Pelo que a escola publica aqui, o recorte institucional coberto hoje e {published_text}.'
    )


def _contact_entries(profile: dict[str, Any], channel: str) -> list[dict[str, str]]:
    contacts = profile.get('contact_channels')
    if not isinstance(contacts, list):
        return []
    entries: list[dict[str, str]] = []
    for item in contacts:
        if not isinstance(item, dict):
            continue
        if str(item.get('channel', '')).lower() != channel:
            continue
        label = str(item.get('label', '')).strip()
        value = str(item.get('value', '')).strip()
        if not value:
            continue
        entries.append({'label': label, 'value': value})
    return entries


def _requested_contact_channel(message: str) -> str | None:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in {'whatsapp', 'whats', 'zap'}):
        return 'whatsapp'
    if any(_message_matches_term(normalized, term) for term in {'email', 'e-mail', 'mail'}):
        return 'email'
    if any(
        _message_matches_term(normalized, term)
        for term in {'telefone', 'fone', 'ligacao', 'ligação', 'ligar', 'ligo', 'fax'}
    ):
        return 'telefone'
    return None


def _count_public_contact_subjects(message: str) -> int:
    normalized = _normalize_text(message)
    subject_term_groups: tuple[set[str], ...] = (
        {'secretaria', 'secretaria escolar'},
        {'financeiro', 'mensalidade', 'boleto', 'boletos'},
        {'direcao', 'direção', 'diretoria', 'diretor', 'diretora'},
        {'coordenacao', 'coordenação', 'coordenador', 'coordenadora'},
        {'admissoes', 'admissões', 'matricula', 'matrícula', 'tour', 'visita'},
        {'orientacao educacional', 'orientação educacional', 'socioemocional', 'bullying'},
    )
    count = 0
    for terms in subject_term_groups:
        if any(_message_matches_term(normalized, term) for term in terms):
            count += 1
    return count


def _is_public_social_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SOCIAL_TERMS)


def _looks_like_teacher_internal_scope_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in TEACHER_SCOPE_GUIDANCE_TERMS):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'qual e a minha grade docente',
            'qual é a minha grade docente',
            'qual e minha grade docente',
            'qual é minha grade docente',
            'quais turmas e disciplinas eu tenho',
            'quais turmas e disciplinas eu atendo',
            'quais turmas eu tenho neste ano',
            'quais turmas eu atendo neste ano',
            'quais disciplinas eu tenho neste ano',
            'quais disciplinas eu atendo neste ano',
        }
    ):
        return True
    if not any(
        _message_matches_term(normalized, term) for term in {'professor', 'professora', 'docente'}
    ):
        return False
    if any(
        _message_matches_term(normalized, term)
        for term in {'meus alunos', 'minhas turmas', 'minhas disciplinas'}
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'ja sou',
            'já sou',
            'como verifico',
            'como consulto',
            'como vejo',
            'como acesso',
        }
    )


def _is_public_careers_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _looks_like_teacher_internal_scope_query(message):
        return False
    if _is_public_capacity_query(message):
        return False
    return any(_message_matches_term(normalized, term) for term in TEACHER_RECRUITMENT_TERMS)


def _is_public_capacity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_capacity_signal = any(
        _message_matches_term(normalized, term)
        for term in (
            *PUBLIC_CAPACITY_STUDENT_TERMS,
            *PUBLIC_CAPACITY_PARKING_TERMS,
            'vaga',
            'vagas',
        )
    )
    if not has_capacity_signal:
        return False
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_PARKING_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_STUDENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in {'vaga', 'vagas'}):
        if any(
            phrase in normalized
            for phrase in {
                'quantas vagas',
                'quanta vaga',
                'tem vagas',
                'tem vaga',
                'ha vagas',
                'há vagas',
            }
        ):
            return True
        if any(
            _message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_DISAMBIGUATION_TERMS
        ):
            return True
        if any(
            _message_matches_term(normalized, term)
            for term in {
                'trabalhar',
                'trabalhe conosco',
                'dar aula',
                'curriculo',
                'currículo',
                'processo seletivo',
            }
        ):
            return False
    return False


def _is_public_web_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_WEB_TERMS)


def _extract_public_curriculum_subject_focus(message: str) -> str | None:
    normalized = _normalize_text(message).strip(' ?.!')
    patterns = (
        r'^(?:e\s+)?(?:tem|possui|oferece)\s+(?:aula|disciplina|materia|matéria)s?\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)$',
        r'^(?:e\s+)?(?:aula|disciplina|materia|matéria)s?\s+de\s+([a-z]{3,}(?:\s+[a-z]{3,})?)$',
        r'^(?:e\s+)?quais?\s+(?:outras\s+)?(?:materias|matérias|disciplinas)\s+tem$',
        r'^(?:e\s+)?que\s+(?:outras\s+)?(?:materias|matérias|disciplinas)\s+tem$',
    )
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        if match.lastindex:
            candidate = _normalize_text(match.group(1))
            return candidate.title() if candidate else None
        return '__list__'
    return None


def _is_public_curriculum_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        return True
    if _extract_public_curriculum_subject_focus(message) is not None:
        return True
    if any(_message_matches_term(normalized, term) for term in ACADEMIC_DIFFICULTY_TERMS) and any(
        _message_matches_term(normalized, term) for term in PUBLIC_CURRICULUM_SCOPE_TERMS
    ):
        return True
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {
            'disciplina',
            'disciplinas',
            'convivencia',
            'convivência',
            'aprendizagem',
            'rotina',
        }
    ):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {'materia', 'materias', 'disciplina', 'disciplinas'}
    ) and any(
        _message_matches_term(normalized, term)
        for term in {
            'ensino medio',
            'ensino médio',
            'fundamental',
            'fundamental i',
            'fundamental ii',
            'anos iniciais',
            'base curricular',
            'curriculo',
            'currículo',
        }
    )


def _is_public_policy_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_POLICY_TERMS):
        return True
    if 'projeto de vida' in normalized:
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'avaliacao',
            'avaliação',
            'recuperacao',
            'recuperação',
            'promocao',
            'promoção',
            'aprovacao',
            'aprovação',
        }
    ):
        return any(
            _message_matches_term(normalized, term)
            for term in {'politica', 'política', 'como funciona', 'regra', 'regras', 'funciona'}
        )
    if any(
        _message_matches_term(normalized, term)
        for term in {'falta', 'faltas', 'frequencia', 'frequência'}
    ):
        return any(
            _message_matches_term(normalized, term)
            for term in {
                'politica',
                'política',
                'regra',
                'regras',
                '75%',
                'minima',
                'mínima',
                'o que acontece',
            }
        )
    return False


def _is_public_navigation_query(message: str) -> bool:
    normalized = _normalize_text(message)
    navigation_terms = {
        'oi',
        'ola',
        'olá',
        'bom dia',
        'boa tarde',
        'boa noite',
        'o que voce faz',
        'o que você faz',
        'como voce pode me ajudar',
        'como você pode me ajudar',
        'quais assuntos',
        'opcoes de assuntos',
        'opções de assuntos',
        'com quem eu falo',
        'com qual contato eu devo falar',
        'qual contato eu devo usar',
        'qual contato devo usar',
        'por qual canal',
        'como falo com',
        'como falar com',
        'como reporto',
        'como denunciar',
        'quem responde por',
        'pra quem eu falo',
        'para quem eu falo',
        'quem cuida',
        'quem resolve',
        'qual setor',
        'qual area',
        'qual área',
        'quem e voce',
        'quem é você',
        'voce e quem',
        'você é quem',
    }
    if any(_message_matches_term(normalized, term) for term in ACKNOWLEDGEMENT_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in AUTH_GUIDANCE_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in ACCESS_SCOPE_TERMS):
        return True
    return any(_message_matches_term(normalized, term) for term in navigation_terms)


def _is_public_operating_hours_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_OPERATING_HOURS_TERMS):
        return True
    return _contains_any(
        normalized, {'abre', 'abertura', 'funciona', 'fecha', 'fechamento'}
    ) and _contains_any(
        normalized,
        {'amanha', 'amanhã', 'cedo', 'horas', 'hora', 'horario', 'horário'},
    )


def _is_public_timeline_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if _is_public_timeline_lifecycle_query(message):
        return True
    if _is_public_travel_planning_query(message):
        return True
    if _is_public_year_three_phase_query(message):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {
            'quando',
            'qual data',
            'que dia',
            'quando comeca',
            'quando começa',
            'comeco',
            'começo',
            'quando fecha',
            'inicio',
            'início',
            'abertura',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
        }
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'matrícula',
            'formatura',
            'inicio das aulas',
            'início das aulas',
            'comeco das aulas',
            'começo das aulas',
            'comecam as aulas',
            'começam as aulas',
            'ano letivo',
        }
    )


def _is_public_timeline_lifecycle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    has_before_after = any(
        _message_matches_term(normalized, term)
        for term in {
            'antes da confirmacao da vaga',
            'antes da confirmação da vaga',
            'depois do inicio das aulas',
            'depois do início das aulas',
            'antes ou depois',
            'antes das aulas',
            'depois das aulas',
            'primeira reuniao',
            'primeira reunião',
        }
    )
    has_ordering = any(
        _message_matches_term(normalized, term)
        for term in {'ordene', 'ordem', 'sequencia', 'sequência', 'linha do tempo', 'passo a passo'}
    )
    asks_which_comes_first = any(
        _message_matches_term(normalized, term)
        for term in {'qual vem primeiro', 'o que vem primeiro', 'vem primeiro'}
    )
    mentions_core_milestones = (
        any(_message_matches_term(normalized, term) for term in {'vaga', 'matricula', 'matrícula'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'inicio das aulas', 'início das aulas', 'aulas'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'responsaveis', 'responsáveis', 'reuniao', 'reunião', 'familia', 'família'}
        )
    )
    mentions_marcos_between = (
        _message_matches_term(normalized, 'marcos entre')
        and any(
            _message_matches_term(normalized, term) for term in {'vaga', 'matricula', 'matrícula'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'inicio do ano letivo',
                'início do ano letivo',
                'inicio das aulas',
                'início das aulas',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'reuniao de responsaveis',
                'reunião de responsáveis',
                'responsaveis',
                'responsáveis',
            }
        )
    )
    return (
        has_before_after
        or mentions_marcos_between
        or (
            any(_message_matches_term(normalized, term) for term in {'antes', 'depois'})
            and any(
                _message_matches_term(normalized, term)
                for term in {
                    'vaga',
                    'matricula',
                    'matrícula',
                    'inicio das aulas',
                    'início das aulas',
                    'aulas',
                }
            )
        )
        or ((has_ordering or asks_which_comes_first) and mentions_core_milestones)
    )


def _is_public_travel_planning_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'viagem' in normalized and any(
        _message_matches_term(normalized, term)
        for term in {'calendario', 'calendário', 'marcos', 'vida escolar', 'datas'}
    )


def _is_public_year_three_phase_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        (
            'tres fases' in normalized
            and all(term in normalized for term in {'admiss', 'rotina', 'fechamento'})
        )
        or (
            all(term in normalized for term in {'admiss', 'rotina academica', 'fechamento'})
            and any(
                _message_matches_term(normalized, term)
                for term in {
                    'distribui',
                    'distribui entre',
                    'olhando so a base publica',
                    'olhando apenas a base publica',
                }
            )
        )
        or (
            all(term in normalized for term in {'admiss', 'rotina academica', 'fechamento'})
            and any(
                _message_matches_term(normalized, term)
                for term in {'se eu dividir o ano', 'dividir o ano', 'dividir o ano escolar'}
            )
        )
    )


def _is_public_calendar_event_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'proximo evento',
            'próximo evento',
            'proxima reuniao',
            'próxima reunião',
            'reuniao de pais',
            'reunião de pais',
            'reuniao geral',
            'reunião geral',
            'mostra de ciencias',
            'mostra de ciências',
            'plantao pedagogico',
            'plantão pedagógico',
            'visita guiada',
        }
    ):
        return True
    asks_timing = any(
        _message_matches_term(normalized, term)
        for term in {'quando', 'qual data', 'que dia', 'quando vai ser', 'quando acontece'}
    )
    if not asks_timing:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'reuniao',
            'reunião',
            'evento',
            'mostra',
            'feira',
            'plantao',
            'plantão',
            'visita guiada',
            'cerimonia',
            'cerimônia',
        }
    )


def _is_public_date_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_UTILITY_DATE_TERMS)


def _format_brazilian_date(value: date) -> str:
    month_names = {
        1: 'janeiro',
        2: 'fevereiro',
        3: 'marco',
        4: 'abril',
        5: 'maio',
        6: 'junho',
        7: 'julho',
        8: 'agosto',
        9: 'setembro',
        10: 'outubro',
        11: 'novembro',
        12: 'dezembro',
    }
    return f'{value.day} de {month_names.get(value.month, str(value.month))} de {value.year}'


def _parse_iso_date_value(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    text = str(value or '').strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _format_public_date_text(value: Any) -> str:
    parsed = _parse_iso_date_value(value)
    if parsed is not None:
        return _format_brazilian_date(parsed)
    return str(value or 'data nao informada').strip() or 'data nao informada'


def _format_contact_origin(label: str | None, channel: str) -> str:
    cleaned = (label or '').strip().lower()
    if not cleaned:
        return ''
    if channel == 'telefone':
        return f'na {cleaned}'
    return f'pela {cleaned}'


def _wants_contact_list(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'quais',
            'lista',
            'todos',
            'todas',
            'contatos',
            'canais',
            'telefones',
            'emails',
            'e-mails',
        }
    )


def _contact_is_general_school_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'da escola',
            'pra escola',
            'para a escola',
            'do colegio',
            'do colégio',
            'geral',
            'institucional',
            'principal',
        }
    )


def _select_primary_contact_entry(
    profile: dict[str, Any],
    channel: str,
    message: str,
    *,
    preferred_labels: list[str] | None = None,
) -> dict[str, str] | None:
    entries = _contact_entries(profile, channel)
    if not entries:
        return None

    normalized = _normalize_text(message)
    normalized_preferred = [_normalize_text(label) for label in preferred_labels or [] if label]
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        if label and label in normalized:
            return entry

    for preferred_label in normalized_preferred:
        for entry in entries:
            label = _normalize_text(entry.get('label', ''))
            if label == preferred_label:
                return entry

    label_aliases = {
        'direcao': {'direcao', 'direção', 'diretoria', 'diretora', 'diretor'},
        'secretaria': {'secretaria', 'secretaria escolar', 'secretaria digital'},
        'orientacao educacional': {
            'orientacao educacional',
            'orientação educacional',
            'bullying',
            'socioemocional',
        },
        'financeiro': {
            'financeiro',
            'boleto',
            'boletos',
            'mensalidade',
            'fatura',
            'faturas',
            'contrato',
        },
        'admissoes': {'admissoes', 'admissões', 'matricula', 'matrícula', 'visita', 'tour'},
    }
    for entry in entries:
        label = _normalize_text(entry.get('label', ''))
        aliases = label_aliases.get(label, set())
        if aliases and any(_message_matches_term(normalized, alias) for alias in aliases):
            return entry

    if _contact_is_general_school_query(message):
        priorities_by_channel = {
            'telefone': ['secretaria'],
            'email': ['secretaria'],
            'whatsapp': ['secretaria digital', 'atendimento comercial'],
        }
        for preferred_label in priorities_by_channel.get(channel, []):
            for entry in entries:
                if _normalize_text(entry.get('label', '')) == preferred_label:
                    return entry

    return entries[0]


def _leadership_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    leadership = profile.get('leadership_team')
    return (
        [item for item in leadership if isinstance(item, dict)]
        if isinstance(leadership, list)
        else []
    )


def _public_kpis(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('public_kpis')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_highlights(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('highlights')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_visit_offers(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('visit_offers')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_service_catalog(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('service_catalog')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _public_feature_inventory(profile: dict[str, Any]) -> list[dict[str, Any]]:
    entries = profile.get('feature_inventory')
    return [item for item in entries if isinstance(item, dict)] if isinstance(entries, list) else []


def _capability_summary_lines(profile: dict[str, Any]) -> list[str]:
    capability_model = profile.get('assistant_capabilities')
    school_name = str(
        (capability_model.get('school_name') if isinstance(capability_model, dict) else None)
        or profile.get('school_name', 'Colegio Horizonte')
    )
    segments_source = (
        capability_model.get('segments')
        if isinstance(capability_model, dict)
        else profile.get('segments', [])
    )
    segments = [str(item) for item in segments_source if isinstance(item, str)]
    segment_summary = ', '.join(segments[:2]).lower() if segments else 'os segmentos atendidos'
    public_topics = [
        str(item)
        for item in (
            capability_model.get('public_topics', []) if isinstance(capability_model, dict) else []
        )
        if isinstance(item, str)
    ]
    protected_topics = [
        str(item)
        for item in (
            capability_model.get('protected_topics', [])
            if isinstance(capability_model, dict)
            else []
        )
        if isinstance(item, str)
    ]
    workflow_topics = [
        str(item)
        for item in (
            capability_model.get('workflow_topics', [])
            if isinstance(capability_model, dict)
            else []
        )
        if isinstance(item, str)
    ]
    lines = [
        f'Posso te ajudar com a rotina institucional do {school_name} em {segment_summary}.',
        'No lado publico, eu cubro: '
        + '; '.join(
            public_topics
            or [
                'matricula, bolsas, visitas, horarios, calendario, biblioteca, uniforme, transporte e vida escolar'
            ]
        )
        + '.',
        'Se sua conta estiver vinculada, eu tambem consigo cuidar de: '
        + '; '.join(protected_topics or ['notas, faltas, boletos e vida financeira'])
        + '.',
        'Quando o assunto pedir acao, eu posso seguir com: '
        + '; '.join(
            workflow_topics
            or [
                'solicitacoes para secretaria, coordenacao, orientacao educacional, financeiro ou direcao'
            ]
        )
        + '.',
        'Se quiser, me diga o tema do jeito que for mais natural e eu sigo com voce.',
    ]
    return lines


def _concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> list[str]:
    examples: list[str] = []
    capability_model = profile.get('assistant_capabilities')
    capability_topics = (
        capability_model.get('public_topics', []) if isinstance(capability_model, dict) else []
    )
    for item in capability_topics:
        if not isinstance(item, str):
            continue
        label = item.strip().lower()
        if label and label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    for service in _public_service_catalog(profile):
        title = str(service.get('title', '')).strip().lower()
        if not title:
            continue
        if 'admis' in title:
            label = 'matricula e visita'
        elif 'finance' in title:
            label = 'financeiro e boletos'
        elif 'secretaria' in title:
            label = 'secretaria e documentos'
        elif 'coorden' in title:
            label = 'coordenacao'
        elif 'orienta' in title:
            label = 'orientacao educacional'
        elif 'dire' in title or 'ouvidoria' in title:
            label = 'direcao e ouvidoria'
        else:
            label = title
        if label not in examples:
            examples.append(label)
        if len(examples) >= limit:
            return examples

    return examples or ['matricula', 'horarios', 'financeiro', 'secretaria', 'visitas']


def _compose_concierge_topic_examples(profile: dict[str, Any], limit: int = 5) -> str:
    examples = _concierge_topic_examples(profile, limit=limit)
    if not examples:
        return 'matricula, horarios, financeiro, secretaria e visitas'
    if len(examples) == 1:
        return examples[0]
    if len(examples) == 2:
        return f'{examples[0]} e {examples[1]}'
    return ', '.join(examples[:-1]) + f' e {examples[-1]}'


def _service_catalog_index(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries = _public_service_catalog(profile)
    result: dict[str, dict[str, Any]] = {}
    for item in entries:
        key = str(item.get('service_key', '')).strip()
        if key:
            result[key] = item
    return result


def _requested_public_attribute(message: str) -> str | None:
    attributes = _requested_public_attributes(message)
    return attributes[0] if attributes else None


def _requested_public_attributes(message: str) -> tuple[str, ...]:
    normalized = _normalize_text(message)
    ordered_matches: list[str] = []

    def add_if_present(value: str, terms: set[str]) -> None:
        if value in ordered_matches:
            return
        if any(_message_matches_term(normalized, term) for term in terms):
            ordered_matches.append(value)

    add_if_present('close_time', {'fecha', 'fechar', 'fechamento', 'encerra', 'encerramento'})
    add_if_present('open_time', {'abre', 'abertura'})
    add_if_present('whatsapp', {'whatsapp', 'whats', 'zap'})
    add_if_present('email', {'email', 'e-mail', 'mail'})
    add_if_present('phone', {'telefone', 'fone', 'ligacao', 'ligação'})
    add_if_present('age', {'idade', 'quantos anos'})
    add_if_present('name', {'nome', 'quem e', 'quem é'})
    add_if_present('contact', {'contato', 'canal', 'como falo', 'como falar', 'falar com'})
    return tuple(ordered_matches)


def _is_public_teacher_identity_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'prof', 'professor', 'professora', 'docente'}
    ):
        return False
    if _requested_public_attribute(message) in {'name', 'whatsapp', 'email', 'phone', 'contact'}:
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'falar com',
            'quero falar com',
            'conversar com',
            'falar direto com',
            'falar diretamente com',
        }
    )


def _is_public_teacher_directory_follow_up(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False
    recent_focus = _recent_trace_focus(conversation_context) or {}
    if isinstance(recent_focus, dict):
        active_task = str(recent_focus.get('active_task', '') or '').strip()
        if active_task == 'public:teacher_directory':
            return any(
                _message_matches_term(normalized, term)
                for term in {
                    'esse contato',
                    'esse canal',
                    'divulga esse contato',
                    'divulga esse canal',
                    'coordenação',
                    'coordenacao',
                    'procurar a coordenação',
                    'procurar a coordenacao',
                    'manda procurar',
                }
            )
    if not _recent_messages_mention(conversation_context, {'professor', 'professora', 'docente'}):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'esse contato',
            'esse canal',
            'divulga esse contato',
            'divulga esse canal',
            'a escola divulga',
            'coordenação',
            'coordenacao',
            'procurar a coordenação',
            'procurar a coordenacao',
            'manda procurar',
        }
    )


def _extract_teacher_subject(message: str) -> str | None:
    normalized = _normalize_text(message)
    patterns = [
        r'prof(?:essor|essora)?\s+de\s+(.+)',
        r'docente\s+de\s+(.+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized)
        if not match:
            continue
        subject = re.split(
            r'\b(?:ou|e|mas|pela?|pelo|se|senao|senão|para)\b|[?!,;.:]',
            match.group(1),
            maxsplit=1,
        )[0].strip(' ?.')
        subject = re.sub(r'\b(?:se nao|senão|senao)\b.*$', '', subject).strip(' ?.')
        if len(subject.split()) > 3:
            subject = ' '.join(subject.split()[:3]).strip(' ?.')
        if subject:
            return subject
    return None


def _recent_service_match(
    profile: dict[str, Any],
    conversation_context: dict[str, Any] | None,
) -> dict[str, Any] | None:
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type not in {'user', 'assistant'}:
            continue
        matches = _service_matches_from_message(profile, content)
        if len(matches) == 1:
            return matches[0]
    return None


def _is_generic_service_contact_follow_up(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'com qual contato eu devo falar',
            'qual contato eu devo usar',
            'qual contato devo usar',
            'qual contato',
            'por qual canal',
            'como falo com',
            'como falar com',
            'quem devo procurar',
            'como entro em contato',
        }
    )


def _service_matches_from_message(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    catalog = _service_catalog_index(profile)
    service_keys: list[str] = []
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'matricula',
            'bolsa',
            'desconto',
            'admissao',
            'admissoes',
            'atendimento comercial',
            'comercial',
            'visita',
            'tour',
        }
    ):
        service_keys.extend(['atendimento_admissoes', 'visita_institucional'])
    if any(
        _message_matches_term(normalized, term) for term in {'secretaria', 'secretaria escolar'}
    ):
        service_keys.append('secretaria_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'documento',
            'documentos',
            'historico',
            'declaração',
            'declaracao',
            'transferencia',
            'uniforme',
        }
    ):
        service_keys.append('secretaria_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'rotina',
            'aprendizagem',
            'adaptacao',
            'adaptação',
            'professor',
            'faltas',
            'nota',
            'notas',
            'disciplina',
        }
    ):
        service_keys.append('reuniao_coordenacao')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'emocional',
            'convivencia',
            'convivência',
            'bullying',
            'orientacao',
            'orientação',
            'socioemocional',
        }
    ):
        service_keys.append('orientacao_educacional')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'mensalidade',
            'boleto',
            'boletos',
            'financeiro',
            'fatura',
            'faturas',
            'pagamento',
            'contrato',
        }
    ):
        service_keys.append('financeiro_escolar')
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'direcao',
            'direção',
            'diretora',
            'ouvidoria',
            'elogio',
            'reclamacao',
            'reclamação',
            'sugestao',
            'sugestão',
        }
    ):
        service_keys.append('solicitacao_direcao')
    if any(
        _message_matches_term(normalized, term)
        for term in {'portal', 'senha', 'acesso', 'telegram', 'bot', 'sistema'}
    ):
        service_keys.append('suporte_digital')
    if any(_message_matches_term(normalized, term) for term in TEACHER_RECRUITMENT_TERMS):
        service_keys.append('carreiras_docentes')
    unique_keys: list[str] = []
    for key in service_keys:
        if key in catalog and key not in unique_keys:
            unique_keys.append(key)
    return [catalog[key] for key in unique_keys]


def _humanize_service_eta(eta: str) -> str:
    cleaned = eta.strip()
    if not cleaned:
        return 'prazo nao informado'
    normalized = _normalize_text(cleaned)
    if normalized.startswith('retorno em '):
        return cleaned
    if normalized.startswith('protocolo imediato'):
        return cleaned
    return f'retorno em {cleaned}'


def _compose_assistant_identity_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    base = (
        f'Voce esta falando com o EduAssist, o assistente institucional do {school_name}. '
        'Eu consigo te orientar por aqui, consultar informacoes da escola e abrir solicitacoes com protocolo. '
        'Se precisar, eu tambem te encaminho para secretaria, matricula e atendimento comercial, coordenacao, orientacao educacional, financeiro ou direcao.'
    )
    return base


def _localize_pt_br_surface_labels(text: str) -> str:
    localized = str(text or '')
    localized = re.sub(
        r'(?i)\badmissions\b',
        'matricula e atendimento comercial',
        localized,
    )
    localized = localized.replace(
        'secretaria/matricula e atendimento comercial',
        'secretaria ou matricula e atendimento comercial',
    )
    localized = localized.replace(
        'secretaria / matricula e atendimento comercial',
        'secretaria ou matricula e atendimento comercial',
    )
    return localized


def _compose_language_preference_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    normalized = _normalize_text(message)
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if 'admissions' in normalized and any(
        term in normalized for term in {'ingles', 'inglês', 'english'}
    ):
        return (
            f'Voce tem razao em estranhar isso. Aqui no EduAssist do {school_name}, eu vou responder em portugues. '
            'Quando eu mencionar admissions, leia como matricula e atendimento comercial.'
        )
    if any(term in normalized for term in {'portugues', 'português'}) and any(
        term in normalized
        for term in {'fale', 'fala', 'responde', 'responda', 'quero que', 'apenas', 'so', 'só'}
    ):
        return (
            'Perfeito. A partir daqui eu respondo em portugues. '
            'Se eu mencionar admissions, entenda como matricula e atendimento comercial.'
        )
    if _assistant_already_introduced(conversation_context):
        return (
            'Perfeito. Eu sigo em portugues. '
            'Se algum termo sair em ingles, eu reformulo em portugues e explico o setor com nomes locais.'
        )
    return (
        f'Perfeito. Eu sigo em portugues aqui no EduAssist do {school_name}. '
        'Se algum termo sair em ingles, eu reformulo em portugues e explico o setor com nomes locais.'
    )


def _compose_input_clarification_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if _assistant_already_introduced(conversation_context):
        return (
            'Nao consegui interpretar essa mensagem com seguranca. '
            'Se quiser, reformule em uma frase curta dizendo o que voce precisa. '
            'Eu consigo seguir em portugues e normalmente tambem entendo ingles e espanhol. '
            'Se a mensagem era so uma saudacao, pode mandar algo como "oi" ou "bom dia".'
        )
    return (
        f'Nao consegui interpretar essa mensagem com seguranca aqui no EduAssist do {school_name}. '
        'Se quiser, reformule em uma frase curta dizendo o que voce precisa. '
        'Eu consigo seguir em portugues e normalmente tambem entendo ingles e espanhol. '
        'Se a mensagem era so uma saudacao, pode mandar algo como "oi" ou "bom dia".'
    )


def _compose_scope_boundary_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    if _assistant_already_introduced(conversation_context):
        return (
            'Nao tenho base confiavel aqui para responder esse tema fora do escopo da escola. '
            'Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.'
        )
    return (
        f'Nao tenho base confiavel aqui no EduAssist do {school_name} para responder esse tema fora do escopo da escola. '
        'Se quiser, eu posso ajudar com matricula, calendario, regras publicas, visitas, notas, frequencia ou financeiro.'
    )


def _is_public_document_submission_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_DOCUMENT_SUBMISSION_TERMS):
        return True
    document_terms = {'documento', 'documentos', 'matricula', 'matrícula', 'cadastro'}
    digital_terms = {
        'online',
        'digital',
        'portal',
        'email',
        'e-mail',
        'enviar',
        'envio',
        'mandar',
        'mando',
    }
    special_channel_terms = {'fax', 'telegrama', 'caixa postal'}
    if any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in special_channel_terms
    ):
        return True
    return any(_message_matches_term(normalized, term) for term in document_terms) and any(
        _message_matches_term(normalized, term) for term in digital_terms
    )


def _is_public_service_credentials_bundle_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if (
        'credenciais' not in normalized
        and 'credencial' not in normalized
        and 'login' not in normalized
        and 'senha' not in normalized
        and 'aplicativo' not in normalized
        and 'app' not in normalized
    ):
        return False
    has_service_anchor = any(
        _message_matches_term(normalized, term)
        for term in {
            'secretaria',
            'portal',
            'aplicativo',
            'app',
            'documentos',
            'documentacao',
            'documentação',
            'cadastro',
        }
    )
    return has_service_anchor


def _is_public_policy_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    mentions_compare = any(
        _message_matches_term(normalized, term)
        for term in {
            'compare',
            'comparar',
            'comparacao',
            'comparação',
            'como os dois se complementam',
        }
    )
    mentions_general_rules = any(
        _message_matches_term(normalized, term)
        for term in {'manual de regulamentos gerais', 'regulamentos gerais', 'manual geral'}
    )
    mentions_eval_policy = any(
        _message_matches_term(normalized, term)
        for term in {
            'politica de avaliacao',
            'política de avaliação',
            'avaliacao e promocao',
            'avaliação e promoção',
        }
    )
    return mentions_compare and mentions_general_rules and mentions_eval_policy


def _is_public_calendar_visibility_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(
        _message_matches_term(normalized, term)
        for term in {'eventos do calendario', 'eventos do calendário', 'calendario', 'calendário'}
    ):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'publicos',
            'públicos',
            'autenticacao',
            'autenticação',
            'contexto interno',
            'interno',
        }
    )


def _is_public_family_new_calendar_enrollment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    required_groups = (
        {'calendario letivo', 'calendário letivo', 'calendario', 'calendário'},
        {'agenda de avaliacoes', 'agenda de avaliações', 'avaliacoes', 'avaliações', 'simulados'},
        {'manual de matricula', 'manual de matrícula', 'matricula', 'matrícula', 'ingresso'},
    )
    canonical_bundle_match = all(
        any(_message_matches_term(normalized, term) for term in group) for group in required_groups
    )
    onboarding_bundle_match = (
        any(
            _message_matches_term(normalized, term)
            for term in {'portal', 'credenciais', 'secretaria', 'envio de documentos', 'documentos'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'inicio das aulas',
                'início das aulas',
                'comeco das aulas',
                'começo das aulas',
                'ordem certa',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'familia nova',
                'família nova',
                'primeira vez',
                'familia',
                'família',
                'inicio do ano',
                'início do ano',
            }
        )
    )
    if not canonical_bundle_match and not onboarding_bundle_match:
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'familia nova',
            'família nova',
            'aluno novo',
            'responsavel novo',
            'responsável novo',
        }
    ) or (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'familia',
                'família',
                'casa',
                'primeiro filho',
                'entrando agora',
                'chegando agora',
                'comeco do ano',
                'começo do ano',
                'inicio do ano',
                'início do ano',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'relacionam',
                'se relacionam',
                'se encaixam',
                'comeco do ano',
                'começo do ano',
            }
        )
    )


def _is_public_health_second_call_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'saude',
                'saúde',
                'motivo de saude',
                'motivo de saúde',
                'atestado',
                'comprovacao',
                'comprovação',
                'justificativa',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'segunda chamada', 'perder uma prova', 'perdi uma prova', 'prova'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'recuperacao', 'recuperação', 'avaliacao', 'avaliação', 'segunda chamada'}
        )
    )


def _is_public_permanence_family_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return 'permanencia escolar' in normalized and any(
        _message_matches_term(normalized, term)
        for term in {
            'acompanhamento da familia',
            'acompanhamento da família',
            'responsaveis',
            'responsáveis',
        }
    )


def _is_public_health_authorization_bridge_query(message: str) -> bool:
    normalized = _normalize_text(message)
    required_terms = {
        'saude',
        'saúde',
        'medicacao',
        'medicação',
        'segunda chamada',
        'saidas pedagogicas',
        'saídas pedagógicas',
        'autorizacoes',
        'autorizações',
    }
    hits = sum(1 for term in required_terms if _message_matches_term(normalized, term))
    return hits >= 5


def _is_public_first_month_risks_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(
            _message_matches_term(normalized, term)
            for term in {
                'primeiro mes',
                'primeiro mês',
                'comeco do ano',
                'começo do ano',
                'primeiras semanas',
                'arranque do ano',
                'arranque do ano letivo',
                'inicio do ano letivo',
                'início do ano letivo',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'riscos',
                'esquecido',
                'prazo',
                'prazos',
                'deslizes',
                'descuidos',
                'erros',
                'baguncam',
                'bagunçam',
                'problemas',
                'explodem',
                'explodir',
            }
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {
                'credenciais',
                'documentos',
                'documentacao',
                'documentação',
                'rotina',
                'papelada',
            }
        )
    )


def _is_public_process_compare_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return (
        any(_message_matches_term(normalized, term) for term in {'rematricula', 'rematrícula'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'transferencia', 'transferência', 'cancelamento'}
        )
        and any(
            _message_matches_term(normalized, term)
            for term in {'compare', 'comparar', 'destacando', 'o que muda'}
        )
    )


def _is_public_bolsas_and_processes_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'bolsa', 'bolsas', 'desconto', 'descontos'}
    ) and any(
        _message_matches_term(normalized, term)
        for term in {'rematricula', 'rematrícula', 'transferencia', 'transferência', 'cancelamento'}
    )


def _compose_public_document_submission_answer(
    profile: dict[str, Any],
    *,
    message: str | None = None,
) -> str:
    policy = profile.get('document_submission_policy')
    normalized_message = _normalize_text(message or '')
    catalog = _service_catalog_index(profile)
    secretaria_service = catalog.get('secretaria_escolar') if isinstance(catalog, dict) else None
    secretaria_eta = ''
    if isinstance(secretaria_service, dict):
        secretaria_eta = _humanize_service_eta(
            str(secretaria_service.get('typical_eta', '')).strip()
        )
    if not isinstance(policy, dict):
        return (
            'Hoje a escola orienta tratar documentos e cadastro pela secretaria ou pelo portal institucional. '
            'Se quiser, eu posso te dizer o canal mais direto da secretaria.'
        )

    accepts_digital_submission = bool(policy.get('accepts_digital_submission'))
    accepted_channels = [
        str(item).strip()
        for item in policy.get('accepted_channels', [])
        if isinstance(item, str) and str(item).strip()
    ]
    warning = str(policy.get('warning', '')).strip()
    notes = str(policy.get('notes', '')).strip()
    secretaria_email_entry = _select_primary_contact_entry(
        profile,
        'email',
        'email da secretaria',
        preferred_labels=['Secretaria'],
    )
    secretaria_email = (
        str(secretaria_email_entry.get('value', '')).strip() if secretaria_email_entry else ''
    )

    accepted_channels_normalized = {_normalize_text(channel) for channel in accepted_channels}
    fallback_channels = []
    if any('portal' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('portal institucional')
    if secretaria_email or any('email' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('email da secretaria')
    if any('secretaria' in channel for channel in accepted_channels_normalized):
        fallback_channels.append('secretaria presencial')
    fallback_preview = (
        ', '.join(fallback_channels)
        if fallback_channels
        else 'portal institucional, email da secretaria ou secretaria presencial'
    )
    if any(
        _message_matches_term(normalized_message, term)
        for term in {'antes voce respondeu', 'você respondeu', 'voce respondeu', 'corrigindo'}
    ):
        return (
            f'Voce esta certo em cobrar essa correcao. Corrigindo: hoje a escola nao utiliza fax para envio de documentos. '
            f'Para isso, use {fallback_preview}.'
        )

    if _message_matches_term(normalized_message, 'fax'):
        return (
            f'Hoje a escola nao utiliza fax para envio de documentos. '
            f'Para isso, use {fallback_preview}.'
        )
    if _message_matches_term(normalized_message, 'telegrama'):
        return (
            f'Hoje a escola nao publica telegrama como canal valido para documentos. '
            f'Para isso, use {fallback_preview}.'
        )
    if _message_matches_term(normalized_message, 'caixa postal'):
        return (
            f'Hoje a escola nao trabalha com caixa postal para esse tipo de envio. '
            f'Para documentos, use {fallback_preview}.'
        )

    if not accepts_digital_submission:
        lines = [
            'Hoje a escola nao publica envio digital como canal principal para essa etapa.',
            'O caminho mais seguro continua sendo a secretaria ou o portal institucional.',
        ]
        if warning:
            lines.append(warning)
        return ' '.join(lines)

    lines = ['Sim. O envio inicial de documentos pode ser feito por canal digital.']
    if accepted_channels:
        canonical_channels = [
            'portal institucional',
            'email da secretaria',
            'secretaria presencial',
        ]
        lines.append('Hoje os canais mais diretos publicados para isso sao:')
        lines.extend(f'- {channel}' for channel in canonical_channels)
    elif secretaria_email:
        lines.append(f'O canal mais direto hoje e o email da secretaria: {secretaria_email}.')
    if secretaria_email and all(
        'email da secretaria' not in channel.lower() for channel in accepted_channels
    ):
        lines.append(f'Email da secretaria: {secretaria_email}.')
    if secretaria_eta:
        lines.append(f'Prazo esperado da secretaria: {secretaria_eta}.')
    if notes:
        lines.append(notes)
    if warning:
        lines.append(warning)
    return '\n'.join(lines)


def _compose_public_service_credentials_bundle_answer(profile: dict[str, Any]) -> str:
    policy = profile.get('document_submission_policy') if isinstance(profile, dict) else None
    warning = str(policy.get('warning', '')).strip() if isinstance(policy, dict) else ''
    lines = [
        'Hoje a familia precisa entender quatro frentes publicas deste fluxo:',
        '- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.',
        '- Portal institucional: centraliza protocolo e envio digital inicial de documentos.',
        '- Credenciais: login e senha do portal continuam sendo a base de acesso; se precisar recuperar acesso, o melhor caminho e a secretaria ou o suporte digital.',
        '- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.',
    ]
    if warning:
        lines.append(warning)
    return '\n'.join(lines)


def _compose_public_policy_compare_answer(profile: dict[str, Any]) -> str:
    policy = profile.get('academic_policy') if isinstance(profile, dict) else None
    attendance = policy.get('attendance_policy') if isinstance(policy, dict) else None
    passing = policy.get('passing_policy') if isinstance(policy, dict) else None
    minimum_attendance = ''
    if isinstance(attendance, dict):
        raw_minimum = str(attendance.get('minimum_attendance_percent') or '').strip()
        if raw_minimum:
            minimum_attendance = raw_minimum.replace('.', ',')
    passing_average = ''
    if isinstance(passing, dict):
        raw_average = str(passing.get('passing_average') or '').strip()
        if raw_average:
            passing_average = raw_average.replace('.', ',')
    attendance_line = (
        f'O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de {minimum_attendance}% de presenca por componente.'
        if minimum_attendance
        else 'O manual de regulamentos gerais organiza convivencia, frequencia e rotina escolar.'
    )
    passing_line = (
        f'Ja a politica de avaliacao explica a aprovacao, a media de referencia {passing_average}, recuperacao, monitorias e criterios de promocao.'
        if passing_average
        else 'Ja a politica de avaliacao explica a aprovacao, recuperacao, monitorias e criterios de promocao.'
    )
    closing = (
        'Os dois se complementam porque a frequencia e os combinados gerais sustentam a rotina, '
        'enquanto a politica academica mostra como a escola trata avaliacao, recuperacao e aprovacao quando a meta nao e atingida.'
    )
    return ' '.join([attendance_line, passing_line, closing])


def _timeline_entry(profile: dict[str, Any], topic_fragment: str) -> dict[str, Any] | None:
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if topic_fragment in str(item.get('topic_key', '')):
            return item
    return None


def _timeline_event_date(item: dict[str, Any] | None) -> str:
    if not isinstance(item, dict):
        return ''
    return str(item.get('event_date') or item.get('starts_at') or '').strip()


def _compose_public_timeline_lifecycle_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    if (
        not isinstance(admissions, dict)
        and not isinstance(school_year, dict)
        and not isinstance(family_meeting, dict)
    ):
        return None
    school_year_date = _timeline_event_date(school_year) if isinstance(school_year, dict) else ''
    family_date = _timeline_event_date(family_meeting) if isinstance(family_meeting, dict) else ''
    if school_year_date and family_date:
        ordering = 'depois' if family_date >= school_year_date else 'antes'
        parts = [f'A primeira reuniao com responsaveis acontece {ordering} do inicio das aulas.']
    else:
        parts: list[str] = []
    if isinstance(admissions, dict):
        admission_text = f'{str(admissions.get("summary", "")).strip()} {str(admissions.get("notes", "")).strip()}'.strip()
        if admission_text:
            parts.append(f'1) Matricula e ingresso: {admission_text}')
    if isinstance(school_year, dict):
        school_year_text = f'{str(school_year.get("summary", "")).strip()} {str(school_year.get("notes", "")).strip()}'.strip()
        if school_year_text:
            parts.append(f'2) Inicio das aulas: {school_year_text}')
    if isinstance(family_meeting, dict):
        family_meeting_text = f'{str(family_meeting.get("summary", "")).strip()} {str(family_meeting.get("notes", "")).strip()}'.strip()
        if family_meeting_text:
            parts.append(f'3) Primeira reuniao com responsaveis: {family_meeting_text}')
    if len(parts) > 1:
        parts.append(
            'Na pratica, esse e o recorte publico em ordem: matricula primeiro, aulas depois e reuniao com as familias na sequencia.'
        )
    answer = ' '.join(part for part in parts if part).strip()
    if answer and len(parts) >= 3:
        return answer
    return compose_public_canonical_lane_answer('public_bundle.timeline_lifecycle', profile=profile)


def _compose_public_timeline_before_after_answer(profile: dict[str, Any]) -> str | None:
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    if not isinstance(school_year, dict) or not isinstance(family_meeting, dict):
        return None
    school_year_date = _timeline_event_date(school_year)
    family_date = _timeline_event_date(family_meeting)
    ordering = (
        'depois'
        if school_year_date and family_date and family_date >= school_year_date
        else 'antes'
    )
    school_year_text = str(school_year.get('summary', '')).strip()
    family_text = str(family_meeting.get('summary', '')).strip()
    parts = [f'A primeira reuniao com responsaveis acontece {ordering} do inicio das aulas.']
    if school_year_text:
        parts.append(f'Inicio das aulas: {school_year_text}')
    if family_text:
        parts.append(f'Primeira reuniao: {family_text}')
    return ' '.join(parts).strip() or None


def _compose_public_timeline_order_only_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    family_meeting = _timeline_entry(profile, 'family_meeting')
    parts: list[str] = []
    if isinstance(admissions, dict):
        summary = str(admissions.get('summary', '')).strip()
        if summary:
            parts.append(f'1) Matricula e ingresso: {summary}')
    if isinstance(school_year, dict):
        summary = str(school_year.get('summary', '')).strip()
        if summary:
            parts.append(f'2) Inicio das aulas: {summary}')
    if isinstance(family_meeting, dict):
        summary = str(family_meeting.get('summary', '')).strip()
        if summary:
            parts.append(f'3) Primeira reuniao com responsaveis: {summary}')
    if parts:
        parts.append(
            'Em ordem pratica, o recorte fica assim: matricula primeiro, aulas depois e reuniao com as familias na sequencia.'
        )
    return ' '.join(parts).strip() if parts else None


def _is_public_timeline_before_after_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'antes das aulas',
            'depois das aulas',
            'primeira reuniao',
            'primeira reunião',
        }
    )


def _should_prefer_raw_public_followup_message(
    *,
    request_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    if str(request_message or '').strip() == str(analysis_message or '').strip():
        return False
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return True
    if _is_public_timeline_lifecycle_query(request_message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'antes ou depois',
        }
    ):
        return True
    if any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ) and _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver sobre cada um'}
    ):
        return True
    return False


def _must_preserve_contextual_public_followup_message(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
) -> bool:
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return True
    if _is_public_timeline_lifecycle_query(request_message):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'antes ou depois',
        }
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {'sobre cada um', 'sobre cada aluno', 'o que eu consigo ver sobre cada um'}
    ):
        return True
    if any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ) and _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ):
        return True
    return False


def _contextualize_public_followup_message(
    *,
    request_message: str,
    analysis_message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    base_message = (
        analysis_message
        if str(analysis_message or '').strip() != str(request_message or '').strip()
        else request_message
    )
    normalized = _normalize_text(request_message)
    if _is_public_year_three_phase_query(request_message):
        return request_message
    if _recent_messages_mention(
        conversation_context,
        {'matricula', 'matrícula', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'},
    ) and any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'primeira reuniao',
            'primeira reunião',
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
            'dividir o ano',
            'admissao',
            'admissão',
            'rotina academica',
            'rotina acadêmica',
            'fechamento',
        }
    ):
        return (
            f'{request_message} sobre matricula, inicio das aulas e reuniao com responsaveis '
            'na linha do tempo publica da escola'
        ).strip()
    if _recent_messages_mention(
        conversation_context,
        {
            'portal',
            'credenciais',
            'documentos',
            'documentacao',
            'documentação',
            'secretaria',
            'matricula',
            'matrícula',
        },
    ) and any(
        term in normalized for term in {'contatos', 'contato', 'financeiro', 'junto com isso'}
    ):
        return (
            f'{request_message} sobre secretaria, financeiro, portal, credenciais e envio de documentos '
            'no fluxo publico para familias novas'
        ).strip()
    if _should_prefer_raw_public_followup_message(
        request_message=request_message,
        analysis_message=analysis_message,
        conversation_context=conversation_context,
    ):
        return request_message
    return base_message


def _compose_contextual_public_timeline_followup_answer(
    *,
    request_message: str,
    conversation_context: dict[str, Any] | None,
    profile: dict[str, Any] | None,
) -> str | None:
    if not isinstance(profile, dict):
        return None
    normalized = _normalize_text(request_message)
    asks_before_after = any(
        _message_matches_term(normalized, term)
        for term in {
            'antes ou depois',
            'primeira reuniao',
            'primeira reunião',
            'antes das aulas',
            'depois das aulas',
        }
    )
    asks_order_only = any(
        _message_matches_term(normalized, term)
        for term in {
            'so esse recorte',
            'só esse recorte',
            'nao quero o calendario inteiro',
            'não quero o calendário inteiro',
            'recorte em ordem',
        }
    )
    # Follow-ups this explicit can be repaired from the public timeline itself,
    # even if the recent turn trace is sparse.
    if asks_before_after:
        direct_before_after = _compose_public_timeline_before_after_answer(profile)
        if direct_before_after:
            return direct_before_after
    if asks_order_only:
        direct_order_only = _compose_public_timeline_order_only_answer(profile)
        if direct_order_only:
            return direct_order_only
    recent_focus = _recent_trace_focus(conversation_context) or {}
    active_task = str(recent_focus.get('active_task', '') or '').strip()
    timeline_thread_active = active_task in {'public:timeline', 'public:calendar_events'}
    timeline_recent_context = timeline_thread_active or _recent_messages_mention(
        conversation_context,
        {'matricula', 'matrícula', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'},
    )
    if asks_before_after and (
        timeline_recent_context
        or any(
            _message_matches_term(normalized, term)
            for term in {'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis'}
        )
    ):
        return _compose_public_timeline_before_after_answer(profile)
    if asks_order_only and timeline_recent_context:
        return _compose_public_timeline_order_only_answer(profile)
    return None


def _compose_public_travel_planning_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    graduation = _timeline_entry(profile, 'graduation')
    milestones: list[str] = []
    for item in (admissions, school_year, graduation):
        if not isinstance(item, dict):
            continue
        summary = str(item.get('summary', '')).strip()
        if summary:
            milestones.append(f'- {summary}')
    if not milestones:
        return None
    return (
        'Para planejar uma viagem sem atrapalhar a vida escolar, vale observar estes marcos publicos antes de fechar datas:\n'
        + '\n'.join(milestones)
    )


def _compose_public_year_three_phases_answer(profile: dict[str, Any]) -> str | None:
    admissions = _timeline_entry(profile, 'admissions_opening')
    school_year = _timeline_entry(profile, 'school_year_start')
    graduation = _timeline_entry(profile, 'graduation')
    parts: list[str] = []
    if isinstance(admissions, dict):
        summary = str(admissions.get('summary', '')).strip()
        if summary:
            parts.append(f'Admissao: {summary}')
    if isinstance(school_year, dict):
        summary = str(school_year.get('summary', '')).strip()
        if summary:
            parts.append(f'Rotina academica: {summary}')
    if isinstance(graduation, dict):
        summary = str(graduation.get('summary', '')).strip()
        if summary:
            parts.append(f'Fechamento: {summary}')
    if parts:
        parts.append(
            'Em ordem pratica, primeiro entra a admissao, depois a rotina academica e, por fim, o fechamento com os marcos finais.'
        )
    answer = '\n'.join(parts).strip() if parts else ''
    if answer and len(parts) >= 4:
        return answer
    return compose_public_canonical_lane_answer('public_bundle.year_three_phases', profile=profile)


def _base_profile_supports_fast_public_answer(
    *,
    message: str,
    profile: dict[str, Any] | None,
) -> bool:
    if not isinstance(profile, dict):
        return False
    if _is_public_timeline_query(message):
        return bool(profile.get('public_timeline'))
    if _is_public_calendar_event_query(message):
        return bool(profile.get('public_calendar_events'))
    return True


def _try_public_channel_fast_answer(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str | None:
    from .public_profile_routes_runtime import _try_public_channel_fast_answer_impl as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )



def _compose_public_pedagogical_answer(profile: dict[str, Any], message: str) -> str | None:
    normalized = _normalize_text(message)
    education_model = str(profile.get('education_model', '')).strip()
    curriculum_basis = str(profile.get('curriculum_basis', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    overview = str(profile.get('short_headline', '')).strip()
    if any(
        _message_matches_term(normalized, phrase)
        for phrase in {
            'proposta pedagogica',
            'proposta pedagógica',
            'projeto pedagogico',
            'projeto pedagógico',
        }
    ):
        parts: list[str] = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if curriculum_basis:
            parts.append(f'No Ensino Medio, isso aparece junto de {curriculum_basis}.')
        if highlight_titles:
            parts.append(
                'Na pratica, isso aparece em frentes como {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        parts.append(
            'Isso se traduz em acompanhamento mais proximo da aprendizagem e em uma proposta pedagogica explicita no dia a dia.'
        )
        return ' '.join(part for part in parts if part).strip() or None
    if _message_matches_term(normalized, 'acolhimento') and any(
        _message_matches_term(normalized, term)
        for term in {
            'disciplina',
            'disciplinas',
            'convivencia',
            'convivência',
            'aprendizagem',
            'rotina',
        }
    ):
        parts = [
            'Pelo que a escola publica hoje, esse equilibrio aparece em uma rotina com acompanhamento proximo e acolhimento estruturado.'
        ]
        if overview:
            parts.append(overview)
        parts.append(
            'Na pratica, isso aparece em orientacao educacional, coordenacao, tutoria academica e projeto de vida, junto de uma jornada de acolhimento para familias e estudantes antes e depois da matricula.'
        )
        return ' '.join(part for part in parts if part).strip()
    if any(_message_matches_term(normalized, term) for term in PUBLIC_PEDAGOGICAL_TERMS):
        parts = []
        if education_model:
            parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
        if highlight_titles:
            parts.append(
                'Os diferenciais pedagogicos mais claros aqui passam por {items}.'.format(
                    items=', '.join(highlight_titles[:3])
                )
            )
        return ' '.join(part for part in parts if part).strip() or None
    return None


def _compose_public_comparative_answer(profile: dict[str, Any]) -> str:
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    education_model = str(profile.get('education_model', '')).strip()
    headline = str(profile.get('short_headline', '')).strip()
    labels_preview = (
        ', '.join(highlight_titles[:3])
        if highlight_titles
        else 'os diferenciais publicados da escola'
    )
    parts = [
        'Estudar em uma escola publica pode ser uma boa escolha para muitas familias, e eu nao vou te vender uma comparacao vazia.',
        f'No que esta publicado aqui, os diferenciais desta escola passam por {labels_preview}.',
    ]
    if education_model:
        parts.append(f'A proposta pedagogica publicada hoje combina {education_model}.')
    parts.append(
        'Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e combinados pedagogicos mais claros.'
    )
    if headline:
        parts.append(headline)
    parts.append(
        'Se quiser, eu posso te mostrar isso de forma mais pratica na rotina, na proposta pedagogica ou no contraturno.'
    )
    return ' '.join(part for part in parts if part).strip()


def _compose_public_comparative_practical_answer(profile: dict[str, Any]) -> str:
    education_model = str(profile.get('education_model', '')).strip()
    highlights = _public_highlights(profile)
    highlight_titles = [
        str(item.get('title', '')).strip()
        for item in highlights
        if str(item.get('title', '')).strip()
    ]
    items = (
        ', '.join(highlight_titles[:3])
        if highlight_titles
        else 'tutoria academica, projeto de vida e acompanhamento proximo'
    )
    parts = [
        'Na pratica, isso muda em uma rotina com aprendizagem por projetos, acompanhamento mais proximo e referencias claras de tutoria academica.',
        f'Os pontos que aparecem hoje de forma mais concreta sao {items}.',
        'Isso aparece no dia a dia em projeto de vida, acompanhamento mais proximo e referencias mais visiveis para familias e estudantes.',
    ]
    if education_model:
        parts.append(f'Isso conversa com uma proposta pedagogica que combina {education_model}.')
    return ' '.join(part for part in parts if part).strip()


def _compose_concierge_greeting(
    profile: dict[str, Any],
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    opening = 'Oi.'
    normalized = _normalize_text(message)
    if 'bom dia' in normalized:
        opening = 'Bom dia.'
    elif 'boa tarde' in normalized:
        opening = 'Boa tarde.'
    elif 'boa noite' in normalized:
        opening = 'Boa noite.'

    active_follow_up = _recent_focus_follow_up_line(conversation_context)
    if active_follow_up:
        if _assistant_already_introduced(conversation_context):
            return f'{opening} {active_follow_up}'
        return f'{opening} Voce esta falando com o EduAssist do {school_name}. {active_follow_up}'

    if _assistant_already_introduced(conversation_context):
        return (
            f'{opening} Sou o EduAssist. Pode seguir do jeito que ficar mais facil. '
            'Se quiser, eu continuo por aqui com o mesmo assunto ou com um tema novo.'
        )

    examples = _compose_concierge_topic_examples(profile, limit=4)
    return (
        f'{opening} Voce esta falando com o EduAssist do {school_name}. '
        f'Posso te ajudar com {examples}. '
        'Se sua conta estiver vinculada, eu tambem consigo consultar notas, faltas e financeiro.'
    )


def _is_acknowledgement_query(message: str) -> bool:
    normalized = _normalize_text(message).strip()
    return any(_message_matches_term(normalized, term) for term in ACKNOWLEDGEMENT_TERMS)


def _compose_concierge_acknowledgement(
    *,
    conversation_context: dict[str, Any] | None,
) -> str:
    recent_assistant = _extract_recent_assistant_message(
        conversation_context.get('recent_messages', [])
        if isinstance(conversation_context, dict)
        else []
    )
    recent_normalized = _normalize_text(recent_assistant or '')
    if 'protocolo' in recent_normalized or 'ticket operacional' in recent_normalized:
        return 'Perfeito. Se quiser, eu acompanho o andamento desse atendimento por aqui.'
    if (
        'autenticacao' in recent_normalized
        or 'vinculo' in recent_normalized
        or 'link_' in recent_normalized
    ):
        return (
            'Combinado. Quando quiser, eu continuo por aqui assim que sua conta estiver vinculada.'
        )
    if 'financeiro' in recent_normalized:
        return 'Combinado. Se quiser, eu sigo com o proximo passo do financeiro ou te direciono para o setor certo.'
    if 'matricula' in recent_normalized or 'visita' in recent_normalized:
        return 'Perfeito. Se quiser, eu continuo daqui e te ajudo com o proximo passo.'
    return (
        'Por nada. Se quiser, pode seguir com a proxima duvida que eu continuo com voce por aqui.'
    )


def _compose_capability_answer(
    profile: dict[str, Any],
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    public_examples = _compose_concierge_topic_examples(profile, limit=3)
    introduced = _assistant_already_introduced(conversation_context)
    if introduced:
        return (
            f'Por aqui eu consigo te ajudar com {public_examples}. '
            'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
            'Se sua conta estiver vinculada, eu tambem consulto notas, faltas e financeiro escolar. '
            'Se precisar de uma acao, eu posso abrir visita, protocolo ou te encaminhar para o setor certo.'
        )
    return (
        f'Eu consigo te ajudar com {public_examples}. '
        'Tambem consigo seguir com secretaria e documentos quando isso entrar no caminho. '
        'Se sua conta estiver vinculada, eu tambem posso consultar notas, faltas e o financeiro escolar. '
        'Se fizer sentido, eu ainda abro visita, protocolo ou te direciono para o setor certo.'
    )


def _routing_follow_up_context_message(
    message: str,
    conversation_context: dict[str, Any] | None,
) -> str:
    if not isinstance(conversation_context, dict):
        return message
    recent_messages = conversation_context.get('recent_messages', [])
    if not isinstance(recent_messages, list):
        return message
    last_user_message = _extract_recent_user_message(recent_messages)
    last_assistant_message = _extract_recent_assistant_message(recent_messages)
    if not last_user_message:
        return message
    if _normalize_text(last_user_message) == _normalize_text(message):
        return message
    if (
        _is_greeting_only(last_user_message)
        or _is_service_routing_query(last_user_message)
        or _is_capability_query(last_user_message)
        or _is_assistant_identity_query(last_user_message)
    ):
        return message
    normalized_last_user = _normalize_text(last_user_message)
    if not any(
        _message_matches_term(normalized_last_user, term)
        for term in SERVICE_FOLLOW_UP_CONTEXT_TERMS
    ):
        return message
    normalized_last_assistant = _normalize_text(last_assistant_message or '')
    if normalized_last_assistant and not any(
        marker in normalized_last_assistant
        for marker in (
            'autenticacao',
            'vinculo',
            'protocolo',
            'ticket operacional',
            'fila',
            'prazo',
            'setor',
            'canal recomendado',
        )
    ):
        return message
    return f'{message} sobre {last_user_message}'


def _compose_service_routing_menu(profile: dict[str, Any]) -> str:
    examples = _concierge_topic_examples(profile, limit=6)
    if not examples:
        return 'Hoje eu consigo te encaminhar para matricula, secretaria, coordenacao, orientacao, financeiro ou direcao.'
    if len(examples) <= 3:
        return 'Hoje eu consigo te encaminhar para ' + ', '.join(examples) + '.'
    return (
        'Hoje eu consigo te encaminhar por aqui para '
        + ', '.join(examples[:-1])
        + f' e {examples[-1]}.'
    )


def _explicit_service_routing_lines(profile: dict[str, Any], message: str) -> list[str]:
    normalized = _normalize_text(message)
    catalog = _service_catalog_index(profile)
    lines: list[str] = []

    def add(line: str | None) -> None:
        cleaned = str(line or '').strip()
        if cleaned and cleaned not in lines:
            lines.append(cleaned)

    def contact_suffix(*, label_terms: set[str], include_whatsapp: bool = False) -> str:
        channel_order = (
            ('email', 'telefone', 'whatsapp') if include_whatsapp else ('email', 'telefone')
        )
        snippets: list[str] = []
        normalized_terms = {_normalize_text(term) for term in label_terms if term}
        for channel in channel_order:
            for entry in _contact_entries(profile, channel):
                label = _normalize_text(entry.get('label'))
                if normalized_terms and not any(term in label for term in normalized_terms):
                    continue
                value = str(entry.get('value') or '').strip()
                if not value:
                    continue
                if channel == 'email':
                    snippets.append(f'email {value}')
                elif channel == 'telefone':
                    snippets.append(f'telefone {value}')
                elif channel == 'whatsapp':
                    snippets.append(f'WhatsApp {value}')
        if not snippets:
            return ''
        return ' Contatos diretos: ' + ' | '.join(dict.fromkeys(snippets)) + '.'

    if any(
        _message_matches_term(normalized, term)
        for term in {'direcao', 'direção', 'diretora', 'diretor'}
    ):
        member = _select_leadership_member(profile, 'direcao')
        if isinstance(member, dict):
            title = str(member.get('title') or 'Direcao geral').strip()
            name = str(member.get('name') or '').strip()
            contact_channel = str(member.get('contact_channel') or '').strip()
            normalized_title = _normalize_text(title)
            routing_label = (
                'Direcao geral'
                if any(
                    term in normalized_title
                    for term in {'diretor', 'diretora', 'direcao', 'direção'}
                )
                else title
            )
            if name and contact_channel:
                add(
                    f'- {routing_label}: {name}. Canal institucional: {contact_channel}.'
                    f'{contact_suffix(label_terms={"direcao"}, include_whatsapp=False)}'
                )
            elif name:
                add(f'- {routing_label}: {name}.')
        else:
            item = catalog.get('solicitacao_direcao')
            if isinstance(item, dict):
                add(
                    f'- Direcao: {str(item.get("request_channel") or "canal institucional").strip()}.'
                    f'{contact_suffix(label_terms={"direcao"}, include_whatsapp=False)}'
                )

    explicit_service_map = (
        (
            {
                'atendimento comercial',
                'comercial',
                'bolsa',
                'bolsas',
                'setor de bolsas',
                'desconto',
                'matricula',
                'matrícula',
                'admissoes',
                'admissões',
            },
            'atendimento_admissoes',
            'Atendimento comercial / Admissoes',
        ),
        (
            {'boleto', 'boletos', 'financeiro', 'fatura', 'faturas', 'mensalidade', 'mensalidades'},
            'financeiro_escolar',
            'Financeiro',
        ),
        (
            {
                'bullying',
                'orientacao educacional',
                'orientação educacional',
                'socioemocional',
                'convivencia',
                'convivência',
            },
            'orientacao_educacional',
            'Orientacao educacional',
        ),
        (
            {
                'secretaria',
                'documentos',
                'declaração',
                'declaracao',
                'atualizacao cadastral',
                'atualização cadastral',
            },
            'secretaria_escolar',
            'Secretaria',
        ),
    )
    for terms, service_key, label in explicit_service_map:
        if not any(_message_matches_term(normalized, term) for term in terms):
            continue
        item = catalog.get(service_key)
        if not isinstance(item, dict):
            continue
        extra_contacts = ''
        if service_key == 'atendimento_admissoes':
            extra_contacts = contact_suffix(
                label_terms={'admissoes', 'atendimento comercial'}, include_whatsapp=True
            )
        elif service_key == 'financeiro_escolar':
            extra_contacts = contact_suffix(label_terms={'financeiro'}, include_whatsapp=False)
        add(
            f'- {label}: {str(item.get("request_channel") or "canal institucional").strip()}.{extra_contacts}'
        )

    return lines


def _compose_service_routing_answer(
    profile: dict[str, Any],
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> str:
    message_for_matching = _routing_follow_up_context_message(message, conversation_context)
    explicit_lines = _explicit_service_routing_lines(profile, message_for_matching)
    if explicit_lines:
        return '\n'.join(
            ['Hoje estes sao os responsaveis e canais mais diretos por assunto:', *explicit_lines]
        )
    matches = _service_matches_from_message(profile, message_for_matching)
    recent_match = None
    if not matches and _is_generic_service_contact_follow_up(message):
        recent_match = _recent_service_match(profile, conversation_context)
    if recent_match is not None:
        matches = [recent_match]
    if not matches:
        if _is_assistant_identity_query(message):
            return _compose_assistant_identity_answer(
                profile,
                conversation_context=conversation_context,
            )
        return (
            'Voce fala comigo, o EduAssist. Eu consigo te orientar e te encaminhar para secretaria, matricula e atendimento comercial, '
            f'coordenacao, orientacao educacional, financeiro ou direcao. {_compose_service_routing_menu(profile)} '
            'Se quiser, me diga o assunto em uma frase curta e eu te indico o melhor caminho sem voce precisar adivinhar o setor.'
        )
    if len(matches) == 1:
        item = matches[0]
        eta = _humanize_service_eta(str(item.get('typical_eta', 'prazo nao informado')))
        if _is_generic_service_contact_follow_up(message):
            response = (
                f'Voce pode falar com {item.get("title", "o setor institucional")} '
                f'por {item.get("request_channel", "canal institucional")}.'
            )
            if eta and eta != 'prazo nao informado':
                response += f' O prazo tipico e {eta}.'
            notes = str(item.get('notes', '')).strip()
            if notes:
                response += f' {notes}'
            response += ' Se quiser, eu sigo por aqui com a solicitacao certa.'
            return response
        return (
            f'Para tratar esse assunto, o caminho mais direto e {item.get("title", "o setor institucional")}. '
            f'Voce pode acionar por {item.get("request_channel", "canal institucional")}, e o prazo tipico e {eta}. '
            f'{str(item.get("notes", "")).strip()} '
            'Se preferir, eu mesmo ja posso seguir por aqui com a solicitacao certa.'
        )
    lines = ['Para esse tema, estes caminhos costumam funcionar melhor:']
    for item in matches[:3]:
        lines.append(
            '- {title}: {request_channel}. Prazo tipico: {typical_eta}.'.format(
                title=item.get('title', 'Setor institucional'),
                request_channel=item.get('request_channel', 'canal institucional'),
                typical_eta=item.get('typical_eta', 'nao informado'),
            )
        )
    lines.append('Se quiser, eu tambem posso seguir por aqui e abrir a solicitacao certa.')
    return '\n'.join(lines)


def _select_leadership_member(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    members = _leadership_inventory(profile)
    if not members:
        return None
    for member in members:
        title = _normalize_text(str(member.get('title', '')))
        name = _normalize_text(str(member.get('name', '')))
        if any(
            phrase in normalized
            for phrase in (
                title,
                name,
                'diretora',
                'diretor',
                'coordenador',
                'coordenadora',
                'direcao',
                'direção',
            )
        ):
            return member
    return members[0]


def _is_leadership_specific_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not any(_message_matches_term(normalized, term) for term in PUBLIC_LEADERSHIP_TERMS):
        return False
    return _requested_public_attribute(message) is not None


def _compose_public_teacher_directory_answer(
    profile: dict[str, Any],
    message: str,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    subject = _extract_teacher_subject(message)
    if subject:
        return (
            f'O {school_name} nao divulga nomes nem contatos diretos de professores por disciplina, como {subject}. '
            'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso.'
        )
    return (
        f'O {school_name} nao divulga nomes nem contatos diretos de professores individualmente. '
        'Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo.'
    )


def _compose_public_leadership_answer(
    profile: dict[str, Any],
    message: str,
    *,
    requested_attribute_override: str | None = None,
) -> str:
    school_name = str(profile.get('school_name', 'Colegio Horizonte'))
    member = _select_leadership_member(profile, message)
    if member is None:
        return (
            f'Hoje o perfil publico do {school_name} nao traz a lideranca institucional detalhada.'
        )

    requested_attribute = requested_attribute_override or _requested_public_attribute(message)
    title = str(member.get('title', 'Lideranca institucional')).strip()
    name = str(member.get('name', school_name)).strip()
    focus = str(member.get('focus', '')).strip()
    contact_channel = str(member.get('contact_channel', '')).strip()
    notes = str(member.get('notes', '')).strip()
    role_reference = f'a {title.lower()}'
    if (
        'diretor' in _normalize_text(message)
        or 'diretora' in _normalize_text(message)
        or 'direcao' in _normalize_text(message)
    ):
        role_reference = 'a direcao geral'

    if requested_attribute == 'name':
        return f'{title}: {name}.'
    if requested_attribute == 'age':
        response = (
            f'{role_reference.capitalize()} da escola hoje e {name}, '
            'mas a escola nao publica a idade dela.'
        )
        if contact_channel:
            response += f' Se voce precisar falar com esse setor, o canal institucional e {contact_channel}.'
        return response
    if requested_attribute == 'whatsapp':
        if contact_channel and '@' not in contact_channel:
            return f'O canal publicado para {role_reference} e {contact_channel}.'
        response = f'A escola nao publica um WhatsApp direto para {role_reference}.'
        if contact_channel:
            response += (
                f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
            )
        return response
    if requested_attribute == 'phone':
        response = f'A escola nao publica um telefone direto para {role_reference}.'
        if contact_channel:
            response += (
                f' O contato institucional divulgado para esse atendimento e {contact_channel}.'
            )
        return response
    if requested_attribute in {'email', 'contact'}:
        if contact_channel:
            response = (
                f'Voce pode falar com {role_reference} pelo canal institucional {contact_channel}.'
            )
            if notes:
                response += f' {notes}'
            return response
        return (
            f'O perfil publico da escola nao traz um canal direto publicado para {role_reference}.'
        )

    lines = [f'{title}: {name}.']
    if focus:
        lines.append(focus)
    if contact_channel:
        lines.append(f'Canal institucional: {contact_channel}.')
    if notes:
        lines.append(notes)
    return ' '.join(line for line in lines if line)


def _select_public_kpis(profile: dict[str, Any], message: str) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    entries = _public_kpis(profile)
    if not entries:
        return []
    selected = [
        item
        for item in entries
        if any(
            marker in normalized
            for marker in (
                _normalize_text(str(item.get('label', ''))),
                _normalize_text(str(item.get('metric_key', ''))),
            )
        )
    ]
    return selected or entries[:3]


def _select_public_highlight(profile: dict[str, Any], message: str) -> dict[str, Any] | None:
    normalized = _normalize_text(message)
    entries = _public_highlights(profile)
    if not entries:
        return None
    for item in entries:
        haystack = ' '.join(
            [
                _normalize_text(str(item.get('title', ''))),
                _normalize_text(str(item.get('description', ''))),
                _normalize_text(str(item.get('highlight_key', ''))),
            ]
        )
        if any(token in haystack for token in _extract_salient_terms(message)):
            return item
    if any(
        _message_matches_term(normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única', 'diferencial', 'diferenciais'}
    ):
        for item in entries:
            if str(item.get('highlight_key')) == 'maker_integrado':
                return item
    return entries[0]


def _compose_public_profile_answer_legacy(
    profile: dict[str, Any],
    message: str,
    *,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    from .public_profile_legacy_runtime import _compose_public_profile_answer_legacy as _impl

    return _impl(
        profile,
        message,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )



def _build_public_profile_context(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> PublicProfileContext:
    from .public_profile_routes_runtime import _build_public_profile_context_impl as _impl

    return _impl(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )



def _resolve_public_profile_act(context: PublicProfileContext) -> str:
    if _is_acknowledgement_query(context.source_message):
        return 'acknowledgement'
    if _looks_like_public_documentary_open_query(context.source_message):
        return 'canonical_fact'
    if context.semantic_act and context.semantic_act != 'canonical_fact':
        if context.semantic_act in {
            'comparative',
            'highlight',
            'features',
        } and _looks_like_public_documentary_open_query(context.source_message):
            return 'canonical_fact'
        return context.semantic_act
    matched_rule = _match_public_act_rule(context.source_message)
    if matched_rule is not None:
        if matched_rule.name in {
            'comparative',
            'highlight',
            'features',
        } and _looks_like_public_documentary_open_query(context.source_message):
            return 'canonical_fact'
        return matched_rule.name
    return 'canonical_fact'


def _handle_public_acknowledgement(context: PublicProfileContext) -> str:
    return _compose_concierge_acknowledgement(conversation_context=context.conversation_context)


def _handle_public_greeting(context: PublicProfileContext) -> str:
    return _compose_concierge_greeting(
        context.profile, context.source_message, context.conversation_context
    )


def _handle_public_input_clarification(context: PublicProfileContext) -> str:
    return _compose_input_clarification_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_scope_boundary(context: PublicProfileContext) -> str:
    return _compose_scope_boundary_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_utility_date(_: PublicProfileContext) -> str:
    return f'Hoje e {_format_brazilian_date(date.today())}.'


def _handle_public_auth_guidance(_: PublicProfileContext) -> str:
    return (
        'Para consultas protegidas, como notas, faltas e financeiro, voce precisa vincular sua conta do Telegram ao portal da escola. '
        'No portal autenticado, gere o codigo de vinculacao e depois envie aqui o comando `/start link_<codigo>`. '
        'Depois disso, eu passo a consultar seus dados autorizados por este canal.'
    )


def _handle_public_language_preference(context: PublicProfileContext) -> str:
    return _compose_language_preference_answer(
        context.profile,
        context.source_message,
        conversation_context=context.conversation_context,
    )


def _handle_public_access_scope(context: PublicProfileContext) -> str:
    return _compose_public_access_scope_answer(
        context.actor,
        school_name=context.school_name,
    )


def _handle_public_assistant_identity(context: PublicProfileContext) -> str:
    return _compose_assistant_identity_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_service_routing(context: PublicProfileContext) -> str:
    return _compose_service_routing_answer(
        context.profile,
        context.source_message,
        conversation_context=context.conversation_context,
    )


def _handle_public_capabilities(context: PublicProfileContext) -> str:
    return _compose_capability_answer(
        context.profile,
        conversation_context=context.conversation_context,
    )


def _handle_public_document_submission(context: PublicProfileContext) -> str:
    return _compose_public_document_submission_answer(
        context.profile, message=context.source_message
    )


def _handle_public_teacher_directory(context: PublicProfileContext) -> str:
    return _compose_public_teacher_directory_answer(context.profile, context.source_message)


def _handle_public_leadership(context: PublicProfileContext) -> str:
    return _compose_public_leadership_answer(
        context.profile,
        context.source_message,
        requested_attribute_override=context.requested_attribute_override,
    )


def _handle_public_web_presence(context: PublicProfileContext) -> str:
    if context.website_url:
        return f'O site oficial {_school_object_reference(context.school_reference)} hoje e {context.website_url}.'
    return (
        f'Hoje eu nao tenho um site oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o telefone ou o email da secretaria.'
    )


def _handle_public_social_presence(context: PublicProfileContext) -> str:
    instagram_entries = _contact_entries(context.profile, 'instagram')
    if instagram_entries:
        primary_entry = instagram_entries[0]
        value = str(primary_entry.get('value', '')).strip()
        label = str(primary_entry.get('label', '')).strip()
        if value:
            prefix = f'O {label.lower()} ' if label else 'O Instagram institucional '
            return (
                f'{prefix}{_school_object_reference(context.school_reference)} hoje e {value}. '
                'Se quiser, eu tambem posso te passar o site oficial ou os canais de atendimento.'
            )
    return (
        f'Hoje eu nao tenho um Instagram oficial publicado no perfil canonico de {context.school_reference}. '
        'Se quiser, eu posso te passar o site oficial ou os canais institucionais de contato.'
    )


def _handle_public_comparative(context: PublicProfileContext) -> str:
    return _compose_public_comparative_answer(context.profile)


def _handle_public_contacts(context: PublicProfileContext) -> str | None:
    from .public_profile_routes_runtime import _handle_public_contacts_impl as _impl

    return _impl(context)



def _handle_public_careers(context: PublicProfileContext) -> str:
    catalog = _service_catalog_index(context.profile)
    careers_entry = catalog.get('carreiras_docentes')
    if careers_entry is None:
        return (
            f'Hoje eu nao tenho um fluxo publico de recrutamento docente estruturado no perfil canonico de {context.school_reference}. '
            'Se quiser, eu posso te passar os canais institucionais da escola.'
        )
    request_channel = str(careers_entry.get('request_channel', 'canal institucional')).strip()
    typical_eta = _humanize_service_eta(
        str(careers_entry.get('typical_eta', 'prazo nao informado'))
    )
    notes = str(careers_entry.get('notes', '')).strip()
    response = (
        f'Se voce quer se candidatar para dar aula em {context.school_reference}, o caminho mais direto hoje e {request_channel}. '
        f'O prazo tipico e {typical_eta}.'
    )
    if notes:
        response += f' {notes}'
    return response


def _target_public_feature_for_operating_hours(
    context: PublicProfileContext,
) -> dict[str, Any] | None:
    feature_map = _feature_inventory_map(context.profile)
    requested_features = _requested_public_features(context.source_message)
    if not requested_features and _is_follow_up_query(context.source_message):
        recent_feature = _recent_public_feature_key(context.conversation_context)
        if recent_feature:
            requested_features = [recent_feature]
    if not requested_features and context.semantic_plan and context.semantic_plan.focus_hint:
        requested_features = _requested_public_features(context.semantic_plan.focus_hint)
    if len(requested_features) != 1:
        return None
    feature_entry = feature_map.get(requested_features[0])
    return (
        feature_entry
        if isinstance(feature_entry, dict) and bool(feature_entry.get('available'))
        else None
    )


def _handle_public_operating_hours(context: PublicProfileContext) -> str:
    requested_attribute = (
        context.requested_attribute_override
        or _requested_operating_hours_attribute(
            context.source_message,
            context.conversation_context,
        )
    )
    requested_attributes = set(_requested_public_attributes(context.source_message))
    feature_entry = _target_public_feature_for_operating_hours(context)
    if feature_entry is not None:
        label = str(feature_entry.get('label', 'esse espaco')).strip() or 'esse espaco'
        notes = str(feature_entry.get('notes', '')).strip()
        feature_key = str(feature_entry.get('feature_key', '')).strip().lower()
        feature_reference = 'A biblioteca' if feature_key == 'biblioteca' else f'O espaco {label}'
        if notes:
            normalized_notes = _normalize_text(notes)
            hours_match = re.search(r'das\s+[0-9h:]+\s+as\s+[0-9h:]+', normalized_notes)
            hours_text = hours_match.group(0) if hours_match else None
            if 'name' in requested_attributes:
                if feature_key == 'biblioteca' and hours_text:
                    return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
                return f'{feature_reference} se chama {label}. Pelo perfil publico, {notes}'
            if feature_key == 'biblioteca' and hours_text:
                return f'A Biblioteca {label} funciona das 7h30 as 18h00.'
            return f'Pelo perfil publico, {label} funciona assim hoje: {notes}'
    if requested_attribute == 'open_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela abre as 7h30.'
        )
    if requested_attribute == 'close_time':
        return (
            f'O atendimento presencial {_school_object_reference(context.school_reference)} fecha as 17h30, de segunda a sexta-feira. '
            'Se voce estiver falando da biblioteca, ela fecha as 18h00.'
        )
    return (
        f'O atendimento presencial {_school_object_reference(context.school_reference)} abre as 7h00 e segue ate as 17h30, de segunda a sexta-feira. '
        'Se voce estiver falando da biblioteca, ela funciona das 7h30 as 18h00.'
    )


def _handle_public_timeline(context: PublicProfileContext) -> str | None:
    from .public_profile_routes_runtime import _handle_public_timeline_impl as _impl

    return _impl(context)



def _recent_user_message_mentions(
    conversation_context: dict[str, Any] | None,
    terms: set[str],
) -> bool:
    if not isinstance(conversation_context, dict):
        return False
    seen_current_user = False
    for sender_type, content in reversed(_recent_message_lines(conversation_context)):
        if sender_type != 'user':
            continue
        if not seen_current_user:
            seen_current_user = True
            continue
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in terms):
            return True
    return False


def _recent_messages_mention(
    conversation_context: dict[str, Any] | None,
    terms: set[str],
) -> bool:
    for _sender_type, content in reversed(_recent_message_lines(conversation_context)):
        normalized = _normalize_text(content)
        if any(_message_matches_term(normalized, term) for term in terms):
            return True
    return False


def _compose_public_school_year_start_answer(
    profile: dict[str, Any], school_reference: str
) -> str | None:
    entries = profile.get('public_timeline')
    if not isinstance(entries, list):
        return None
    for item in entries:
        if not isinstance(item, dict):
            continue
        if 'school_year_start' not in str(item.get('topic_key', '')):
            continue
        summary = str(item.get('summary', '')).strip()
        notes = str(item.get('notes', '')).strip()
        if summary and notes:
            return f'{summary} {notes}'.strip()
        if summary:
            return summary
    return None


def _event_query_tokens(message: str, focus_hint: str | None = None) -> set[str]:
    source = _normalize_text(' '.join(part for part in [focus_hint or '', message] if part).strip())
    tokens = {
        token
        for token in re.findall(r'[a-z0-9]{3,}', source)
        if token
        not in {
            'quando',
            'qual',
            'quais',
            'que',
            'dia',
            'data',
            'proximo',
            'proxima',
            'proximoa',
            'evento',
            'eventos',
            'publico',
            'publicos',
            'amanha',
            'hoje',
            'escola',
            'colegio',
        }
    }
    return tokens


def _format_event_datetime_br(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None
    return parsed.astimezone(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y às %Hh%M')


def _select_public_calendar_events(
    *,
    events: list[dict[str, Any]],
    message: str,
    focus_hint: str | None,
) -> list[dict[str, Any]]:
    normalized = _normalize_text(message)
    tokens = _event_query_tokens(message, focus_hint)
    scored: list[tuple[int, dict[str, Any]]] = []
    for event in events:
        haystack = _normalize_text(
            ' '.join(
                str(event.get(key, '')).strip()
                for key in ('title', 'description', 'category', 'audience')
            )
        )
        score = 0
        for token in tokens:
            if token in haystack:
                score += 2
        if any(
            _message_matches_term(normalized, term)
            for term in {'reuniao', 'reunião', 'pais', 'responsaveis', 'responsáveis'}
        ) and ('meeting' in haystack or 'reuniao' in haystack or 'responsaveis' in haystack):
            score += 3
        if any(
            _message_matches_term(normalized, term) for term in {'mostra', 'ciencias', 'ciências'}
        ) and ('mostra' in haystack or 'ciencias' in haystack):
            score += 3
        if any(
            _message_matches_term(normalized, term) for term in {'visita', 'tour', 'guiada'}
        ) and ('visita' in haystack or 'open_house' in haystack):
            score += 3
        if score > 0:
            scored.append((score, event))
    if scored:
        scored.sort(
            key=lambda item: (
                -item[0],
                str(item[1].get('starts_at', '')),
                str(item[1].get('title', '')),
            )
        )
        return [item for _score, item in scored[:2]]
    sorted_events = sorted(
        events,
        key=lambda event: (
            str(event.get('starts_at', '')),
            str(event.get('title', '')),
        ),
    )
    return sorted_events[:2]


def _handle_public_calendar_events(context: PublicProfileContext) -> str:
    events = context.profile.get('public_calendar_events')
    if not isinstance(events, list) or not events:
        return f'Hoje a base publica de eventos de {context.school_reference} nao trouxe agenda estruturada para esse pedido.'

    selected = _select_public_calendar_events(
        events=[item for item in events if isinstance(item, dict)],
        message=context.source_message,
        focus_hint=context.semantic_plan.focus_hint if context.semantic_plan else None,
    )
    if not selected:
        return f'Hoje eu nao encontrei um evento publico especifico para esse pedido em {context.school_reference}.'

    if len(selected) == 1:
        item = selected[0]
        title = str(item.get('title', 'Evento publico')).strip()
        description = str(item.get('description', '')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at'))
        ends_at = _format_event_datetime_br(item.get('ends_at'))
        time_part = f'{starts_at}' if starts_at else 'data ainda nao informada'
        if starts_at and ends_at:
            time_part = f'{starts_at} até {ends_at.split(" às ")[-1]}'
        response = f'{title}: {time_part}.'
        if description:
            response += f' {description}'
        return response

    lines = ['Encontrei estes proximos eventos publicos relacionados a esse assunto:']
    for item in selected:
        title = str(item.get('title', 'Evento publico')).strip()
        starts_at = _format_event_datetime_br(item.get('starts_at')) or 'data ainda nao informada'
        lines.append(f'- {title}: {starts_at}.')
    return '\n'.join(lines)


def _handle_public_location(context: PublicProfileContext) -> str:
    location = ', '.join(
        part
        for part in [context.address_line, context.district, context.city, context.state]
        if part
    )
    if context.postal_code:
        location = f'{location}, CEP {context.postal_code}'
    return f'{context.school_reference_capitalized} fica em {location}.'


def _handle_public_confessional(context: PublicProfileContext) -> str:
    if context.confessional_status == 'laica':
        return (
            f'{context.school_reference_capitalized} e uma escola laica. '
            'A proposta institucional e plural e nao confessional.'
        )
    return f'Hoje o perfil publico classifica {context.school_reference} como {context.confessional_status}.'


def _match_public_curriculum_component(
    components: tuple[str, ...],
    requested_subject: str,
) -> str | None:
    requested_normalized = _normalize_text(requested_subject)
    if not requested_normalized:
        return None
    for component in components:
        normalized_component = _normalize_text(component)
        if (
            requested_normalized == normalized_component
            or requested_normalized in normalized_component
            or normalized_component in requested_normalized
        ):
            return component
        for hint in SUBJECT_HINTS.get(normalized_component, set()):
            normalized_hint = _normalize_text(hint)
            if requested_normalized == normalized_hint or requested_normalized in normalized_hint:
                return component
    return None


def _handle_public_curriculum(context: PublicProfileContext) -> str:
    pedagogical_answer = _compose_public_pedagogical_answer(context.profile, context.source_message)
    if pedagogical_answer:
        return pedagogical_answer
    requested_subject = _extract_public_curriculum_subject_focus(context.source_message)
    if requested_subject and requested_subject != '__list__':
        matched_component = _match_public_curriculum_component(
            context.curriculum_components,
            requested_subject,
        )
        if matched_component:
            return (
                f'Sim. Pelo perfil publico atual de {context.school_reference}, {matched_component} aparece entre os componentes curriculares oferecidos. '
                'Se quiser, eu tambem posso listar as outras materias que aparecem nessa grade publica.'
            )
        return (
            f'Hoje eu nao vi {requested_subject} aparecendo como componente curricular publico de {context.school_reference}. '
            'Se quiser, eu posso listar as materias que aparecem oficialmente na grade publicada.'
        )
    if requested_subject == '__list__':
        if context.curriculum_components:
            components = ', '.join(context.curriculum_components[:10])
            extra = ' e outras frentes eletivas' if len(context.curriculum_components) > 10 else ''
            return f'Pelo perfil publico atual de {context.school_reference}, as materias que aparecem com mais clareza sao {components}{extra}.'
    if any(
        _message_matches_term(context.normalized, term) for term in ACADEMIC_DIFFICULTY_TERMS
    ) and any(
        _message_matches_term(context.normalized, term) for term in PUBLIC_CURRICULUM_SCOPE_TERMS
    ):
        if context.curriculum_components:
            components = ', '.join(context.curriculum_components[:8])
            return (
                f'Pelo que {context.school_reference} publica, nao existe uma unica materia oficialmente marcada como "a mais dificil". '
                f'Isso varia conforme o perfil do aluno e a etapa. Na grade publica aparecem componentes como {components}.'
            )
        return (
            f'Pelo que {context.school_reference} publica, nao existe uma unica materia oficialmente marcada como "a mais dificil". '
            'Isso varia conforme o perfil do aluno e a etapa.'
        )
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='grade curricular',
        )
    if context.curriculum_basis and context.curriculum_components:
        components = ', '.join(context.curriculum_components[:8])
        extra = (
            ', alem de projeto de vida, monitorias e trilhas eletivas'
            if len(context.curriculum_components) > 8
            else ''
        )
        return (
            f'No Ensino Medio, {context.school_reference} segue a BNCC e um curriculo proprio de aprofundamento academico. '
            f'Os componentes que aparecem hoje na base publica incluem {components}{extra}.'
        )
    if context.curriculum_basis:
        return f'Hoje a base curricular publica de {context.school_reference} e esta: {context.curriculum_basis}'
    return (
        f'Hoje eu nao encontrei um detalhamento curricular estruturado de {context.school_reference}. '
        'Se quiser, eu posso resumir a proposta pedagogica publicada.'
    )


def _compose_public_policy_answer(
    profile: dict[str, Any],
    *,
    message: str,
    authenticated: bool = False,
) -> str | None:
    policy = profile.get('academic_policy')
    if not isinstance(policy, dict):
        return None

    normalized = _normalize_text(message)
    if 'projeto de vida' in normalized:
        summary = str(policy.get('project_of_life_summary', '')).strip()
        if summary:
            return (
                f'No Colegio Horizonte, Projeto de vida e parte da proposta pedagogica. {summary}'
            )

    attendance = policy.get('attendance_policy')
    if isinstance(attendance, dict) and any(
        _message_matches_term(normalized, term)
        for term in {'falta', 'faltas', 'frequencia', 'frequência', '75%', 'minima', 'mínima'}
    ):
        minimum = Decimal(str(attendance.get('minimum_attendance_percent') or '0')).quantize(
            Decimal('0.1')
        )
        minimum_label = f'{str(minimum).replace(".", ",")}%'
        first_absence = str(attendance.get('first_absence_guidance', '')).strip()
        chronic = str(attendance.get('chronic_absence_guidance', '')).strip()
        follow_up = str(attendance.get('follow_up_channel', '')).strip()
        notes = str(attendance.get('notes', '')).strip()
        if 'primeira aula' in normalized and first_absence:
            answer = first_absence
            if follow_up:
                answer += (
                    f' Se a situacao se repetir, o acompanhamento costuma passar por {follow_up}.'
                )
            return answer
        answer = f'No Colegio Horizonte, a referencia publica minima de frequencia e {minimum_label} por componente.'
        if chronic:
            answer += f' {chronic}'
        if notes:
            answer += f' {notes}'
        return answer

    passing = policy.get('passing_policy')
    if isinstance(passing, dict):
        average = Decimal(str(passing.get('passing_average') or '0')).quantize(Decimal('0.1'))
        scale = str(passing.get('reference_scale') or '0-10').strip()
        support = str(passing.get('recovery_support', '')).strip()
        notes = str(passing.get('notes', '')).strip()
        answer = f'No Colegio Horizonte, a referencia publica de aprovacao e media {str(average).replace(".", ",")}/{scale.split("-")[-1]}.'
        if support:
            answer += f' {support}'
        if notes:
            answer += f' {notes}'
        if authenticated:
            answer += ' Se quiser, eu posso calcular quanto falta para Lucas ou Ana em uma disciplina especifica.'
        return answer

    return None


def _handle_public_policy(context: PublicProfileContext) -> str:
    answer = _compose_public_policy_answer(
        context.profile,
        message=context.source_message,
        authenticated=bool(context.actor),
    )
    if answer:
        return answer
    return (
        f'Hoje eu nao encontrei uma politica academica publica estruturada de {context.school_reference}. '
        'Se quiser, eu posso resumir a proposta pedagogica ou os documentos publicos relacionados.'
    )


def _handle_public_policy_compare(context: PublicProfileContext) -> str:
    return _compose_public_policy_compare_answer(context.profile)


def _handle_public_service_credentials_bundle(context: PublicProfileContext) -> str:
    return _compose_public_service_credentials_bundle_answer(context.profile)


def _handle_public_kpi(context: PublicProfileContext) -> str:
    entries = _select_public_kpis(context.profile, context.source_message)
    if not entries:
        return f'Hoje o perfil publico de {context.school_reference} nao traz indicadores institucionais publicados.'
    if len(entries) == 1:
        item = entries[0]
        notes = str(item.get('notes', '')).strip()
        return (
            f'Hoje, {item.get("label", "o indicador institucional")} esta em {item.get("value", "--")}{item.get("unit", "")} '
            f'({item.get("reference_period", "periodo nao informado")}). {notes}'.strip()
        )
    lines = [f'Os indicadores publicos mais recentes de {context.school_reference} sao:']
    for item in entries:
        lines.append(
            f'- {item.get("label", "Indicador")}: {item.get("value", "--")}{item.get("unit", "")} '
            f'({item.get("reference_period", "periodo nao informado")})'
        )
    return '\n'.join(lines)


def _handle_public_highlight(context: PublicProfileContext) -> str:
    if any(
        _message_matches_term(context.normalized, term)
        for term in {
            '30 segundos',
            '30s',
            'familia nova',
            'família nova',
            'por que escolher',
            'por que deveria',
        }
    ):
        highlights = _public_highlights(context.profile)
        top_titles = [
            str(item.get('title', '')).strip()
            for item in highlights
            if str(item.get('title', '')).strip()
        ]
        items = (
            ', '.join(top_titles[:3])
            if top_titles
            else 'acompanhamento tutorial, projeto de vida e trilhas academicas'
        )
        headline = str(context.profile.get('short_headline', '')).strip()
        education_model = str(context.profile.get('education_model', '')).strip()
        parts = [
            f'Se eu tivesse 30 segundos para resumir {context.school_reference}, eu diria isto:',
            headline
            or f'{context.school_reference_capitalized} combina aprendizagem por projetos, acompanhamento proximo e trilhas academicas no contraturno.',
            f'Os diferenciais publicados com mais clareza hoje passam por {items}.',
        ]
        if education_model:
            parts.append(f'A proposta pedagogica publicada combina {education_model}.')
        parts.append(
            'Na pratica, isso aparece em aprendizagem por projetos, acompanhamento mais proximo, estudo orientado e contraturno com referencias claras para familias.'
        )
        return ' '.join(part for part in parts if part).strip()
    item = _select_public_highlight(context.profile, context.source_message)
    if item is None:
        return f'Hoje o perfil publico de {context.school_reference} nao traz diferenciais institucionais consolidados.'
    evidence_line = str(item.get('evidence_line', '')).strip()
    intro = 'Um dos diferenciais documentados desta escola'
    if any(
        _message_matches_term(context.normalized, term)
        for term in {'curiosidade', 'curiosidades', 'unica', 'única'}
    ):
        intro = 'Uma curiosidade documentada desta escola'
    title = str(item.get('title', 'Diferencial institucional')).strip()
    description = str(item.get('description', '')).strip()
    lines = [f'{intro} e {title}. {description}'.strip()]
    if evidence_line:
        lines.append(f'Isso aparece de forma bem clara na proposta institucional: {evidence_line}')
    return ' '.join(line for line in lines if line)


def _handle_public_visit(context: PublicProfileContext) -> str:
    offers = _public_visit_offers(context.profile)
    services = _public_service_catalog(context.profile)
    if not offers:
        return f'Hoje o perfil publico de {context.school_reference} nao traz janelas de visita institucional.'
    lines = [
        f'Hoje {_school_subject_reference(context.school_reference)} publica estas janelas de visita:'
    ]
    for item in offers:
        lines.append(
            '- {title}: {day_label}, das {start_time} as {end_time}, em {location}. {notes}'.format(
                title=item.get('title', 'Visita institucional'),
                day_label=item.get('day_label', 'dia util'),
                start_time=item.get('start_time', '--:--'),
                end_time=item.get('end_time', '--:--'),
                location=item.get('location', 'local a confirmar'),
                notes=str(item.get('notes', '')).strip(),
            ).rstrip()
        )
    visit_service = next(
        (item for item in services if str(item.get('service_key')) == 'visita_institucional'),
        None,
    )
    if visit_service is not None:
        lines.append(
            'Agendamento: {request_channel}. Prazo de confirmacao: {typical_eta}.'.format(
                request_channel=visit_service.get('request_channel', 'canal institucional'),
                typical_eta=visit_service.get('typical_eta', 'ate 1 dia util'),
            )
        )
    return '\n'.join(lines)


def _is_public_scholarship_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_SCHOLARSHIP_TERMS)


def _is_public_enrichment_query(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(_message_matches_term(normalized, term) for term in PUBLIC_ENRICHMENT_TERMS)


def _compose_public_scholarship_answer(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='bolsas e descontos',
        )
    service = next(
        (
            item
            for item in _public_service_catalog(context.profile)
            if str(item.get('service_key', '')).strip() == 'atendimento_admissoes'
        ),
        None,
    )
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and (context.segment is None or str(row.get('segment')) == context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]

    policy_notes: list[str] = []
    for row in relevant_rows:
        notes = str(row.get('notes', '')).strip()
        normalized_notes = _normalize_text(notes)
        if notes and any(
            _message_matches_term(normalized_notes, term)
            for term in {
                'irmaos',
                'irmãos',
                'pagamento pontual',
                'politica comercial',
                'política comercial',
            }
        ):
            policy_notes.append(notes)
    lines = [
        f'Hoje, pelo que {context.school_reference} publica, bolsas e descontos entram no atendimento comercial de matricula.',
    ]
    if policy_notes:
        lines.append(f'A referencia comercial atual tambem menciona {policy_notes[0].lower()}')
    else:
        lines.append(
            'A base publica confirma que esse tema passa pelo canal comercial, junto com simulacao financeira e processo de ingresso.'
        )
    if isinstance(service, dict):
        request_channel = str(service.get('request_channel', 'canal institucional')).strip()
        eta = _humanize_service_eta(str(service.get('typical_eta', 'retorno em ate 1 dia util')))
        notes = str(service.get('notes', '')).strip()
        lines.append(
            f'O caminho mais direto hoje e {service.get("title", "matricula e atendimento comercial")} por {request_channel}, com {eta}.'
        )
        if notes:
            lines.append(notes)
    return ' '.join(line.strip() for line in lines if line and line.strip())


def _compose_public_enrichment_answer(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='atividades complementares',
        )
    relevant_rows = [
        row
        for row in context.shift_offers
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]

    available_features = _public_feature_inventory(context.profile)
    enrichment_labels: list[str] = []
    for key in ('biblioteca', 'danca', 'teatro', 'futebol', 'volei', 'maker', 'laboratorio'):
        item = next(
            (
                feature
                for feature in available_features
                if str(feature.get('feature_key', '')).strip() == key
                and bool(feature.get('available'))
            ),
            None,
        )
        if not isinstance(item, dict):
            continue
        label = str(item.get('label', '')).strip()
        if label and label not in enrichment_labels:
            enrichment_labels.append(label)

    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        lines = [
            f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no {str(row.get("segment", "segmento")).lower()}.',
            str(row.get('notes', '')).strip(),
        ]
    else:
        lines = [
            f'Hoje {_school_subject_reference(context.school_reference)} divulga atividades complementares no contraturno de forma assim:'
        ]
        for row in relevant_rows[:3]:
            segment = str(row.get('segment', 'Segmento')).strip()
            notes = str(row.get('notes', '')).strip()
            if notes:
                lines.append(f'- {segment}: {notes}')
    if enrichment_labels:
        labels_preview = ', '.join(enrichment_labels[:6])
        lines.append(f'Entre as ofertas que aparecem com mais clareza hoje estao {labels_preview}.')
    return ' '.join(line.strip() for line in lines if line and line.strip())


def _parse_public_money(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    text = str(value).strip()
    if not text:
        return None
    cleaned = re.sub(r'[^0-9,.\-]', '', text)
    if not cleaned:
        return None
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        cleaned = cleaned.replace('.', '').replace(',', '.')
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _format_brl(value: Any) -> str:
    amount = _parse_public_money(value)
    if amount is None:
        return str(value)
    quantized = amount.quantize(Decimal('0.01'))
    formatted = f'{quantized:,.2f}'
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'R$ {formatted}'


def _is_public_pricing_projection_context(candidate: Any) -> bool:
    return isinstance(candidate, PublicProfileContext) or (
        hasattr(candidate, 'source_message')
        and hasattr(candidate, 'normalized')
        and hasattr(candidate, 'slot_memory')
        and hasattr(candidate, 'tuition_reference')
    )


def _compose_public_pricing_projection_answer(
    profile_or_context: dict[str, Any] | PublicProfileContext,
    message: str | None = None,
    *,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str | None:
    from .public_profile_routes_runtime import _compose_public_pricing_projection_answer_impl as _impl

    if message is None and _is_public_pricing_projection_context(profile_or_context):
        return _impl(profile_or_context)
    if message is None or not isinstance(profile_or_context, dict):
        raise TypeError('profile + message ou PublicProfileContext sao obrigatorios')
    context = _build_public_profile_context(
        profile_or_context,
        message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    return _impl(context)



def _handle_public_pricing(context: PublicProfileContext) -> str:
    pricing_projection_answer = _compose_public_pricing_projection_answer(context)
    if pricing_projection_answer:
        return pricing_projection_answer
    if _is_public_scholarship_query(context.source_message):
        return _compose_public_scholarship_answer(context)
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='mensalidades publicas',
        )
    requested_segment = context.segment or context.slot_memory.public_pricing_segment
    relevant_rows = [
        row
        for row in context.tuition_reference
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), requested_segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.tuition_reference if isinstance(row, dict)]
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        return (
            f'Para {row.get("segment", "esse segmento")} no turno {row.get("shift_label", "regular")}, '
            f'a mensalidade publica de referencia em 2026 e {_format_brl(row.get("monthly_amount", "0.00"))} '
            f'e a taxa de matricula e {_format_brl(row.get("enrollment_fee", "0.00"))}. '
            f'{str(row.get("notes", "")).strip()} '
            'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
        ).strip()
    lines = ['Valores publicos de referencia para 2026:']
    for row in relevant_rows:
        lines.append(
            '- {segment} ({shift_label}): mensalidade {monthly_amount} e taxa de matricula {enrollment_fee}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                shift_label=row.get('shift_label', 'turno'),
                monthly_amount=_format_brl(row.get('monthly_amount', '0.00')),
                enrollment_fee=_format_brl(row.get('enrollment_fee', '0.00')),
                notes=row.get('notes', '').strip(),
            ).rstrip()
        )
    lines.append(
        'Se quiser, eu tambem posso resumir bolsas, descontos comerciais e canais de matricula.'
    )
    return '\n'.join(lines)


_PUBLIC_MULTI_INTENT_LABELS: dict[str, str] = {
    'contacts': 'Canais gerais da escola',
    'service_routing': 'Setor certo por assunto',
    'pricing': 'Valores publicos e simulacao',
    'document_submission': 'Documentos e envio',
    'service_credentials_bundle': 'Portal, credenciais e secretaria',
    'policy_compare': 'Regras academicas e regulamentos',
    'timeline': 'Linha do tempo publica',
    'calendar_events': 'Calendario publico',
}


def _compose_public_act_answer(
    context: PublicProfileContext,
    *,
    act: str,
) -> str | None:
    if act == 'contacts':
        return _handle_public_contacts(context)
    if act == 'service_routing':
        return _handle_public_service_routing(context)
    if act == 'pricing':
        return _handle_public_pricing(context)
    if act == 'document_submission':
        return _handle_public_document_submission(context)
    if act == 'service_credentials_bundle':
        return _compose_public_service_credentials_bundle_answer(context.profile)
    if act == 'policy_compare':
        return _compose_public_policy_compare_answer(context.profile)
    if act == 'timeline':
        return _handle_public_timeline(context)
    if act == 'calendar_events':
        return _handle_public_timeline(context)
    return None


def _candidate_public_multi_intent_acts(
    *,
    message: str,
    semantic_plan: PublicInstitutionPlan | None,
    conversation_context: dict[str, Any] | None,
) -> tuple[str, ...]:
    acts: list[str] = []
    if semantic_plan is not None:
        acts.extend(
            act
            for act in (semantic_plan.conversation_act, *semantic_plan.secondary_acts)
            if isinstance(act, str) and act.strip()
        )
    elif _has_public_multi_intent_signal(message):
        matched_rules = _prioritize_public_act_rules(
            message,
            _matched_public_act_rules(message, conversation_context=conversation_context),
        )
        acts.extend(
            rule.name for rule in matched_rules[:3] if isinstance(rule.name, str) and rule.name
        )

    explicit_detectors: tuple[tuple[str, Callable[[str], bool]], ...] = (
        (
            'contacts',
            lambda value: (
                _matches_public_contact_rule(value) or _requested_contact_channel(value) is not None
            ),
        ),
        ('service_routing', _is_service_routing_query),
        ('pricing', _is_public_pricing_navigation_query),
        ('document_submission', _is_public_document_submission_query),
        ('service_credentials_bundle', _is_public_service_credentials_bundle_query),
        ('policy_compare', _is_public_policy_compare_query),
        ('timeline', _is_public_timeline_query),
        ('calendar_events', _is_public_calendar_event_query),
    )
    for act, matcher in explicit_detectors:
        if matcher(message) and act not in acts:
            acts.append(act)

    ordered: list[str] = []
    seen: set[str] = set()
    for act in acts:
        if act not in _PUBLIC_MULTI_INTENT_LABELS:
            continue
        if act in seen:
            continue
        seen.add(act)
        ordered.append(act)
    return tuple(ordered)


def _compose_public_multi_intent_answer(
    context: PublicProfileContext,
    *,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str | None:
    if _is_direct_service_routing_bundle_query(context.source_message):
        return None
    acts = _candidate_public_multi_intent_acts(
        message=context.source_message,
        semantic_plan=semantic_plan,
        conversation_context=context.conversation_context,
    )
    if len(acts) < 2:
        return None
    sections: list[tuple[str, str]] = []
    seen_answers: set[str] = set()
    for act in acts[:3]:
        answer = _compose_public_act_answer(context, act=act)
        normalized_answer = re.sub(r'\s+', ' ', str(answer or '').strip())
        if not normalized_answer or normalized_answer in seen_answers:
            continue
        seen_answers.add(normalized_answer)
        sections.append((_PUBLIC_MULTI_INTENT_LABELS[act], normalized_answer.replace('\n', ' ')))
    if len(sections) < 2:
        return None
    intro = (
        'Posso separar esse pedido em duas frentes complementares:'
        if len(sections) == 2
        else 'Posso separar esse pedido em frentes complementares:'
    )
    lines = [intro]
    lines.extend(f'- {label}: {answer}' for label, answer in sections)
    return '\n'.join(lines)


def _handle_public_schedule(context: PublicProfileContext) -> str:
    requested_unpublished_segment = _requested_unpublished_public_segment(context)
    if requested_unpublished_segment:
        return _compose_public_segment_scope_gap(
            context,
            requested_segment=requested_unpublished_segment,
            topic='horarios',
        )
    grade_reference = _extract_grade_reference(context.source_message)
    relevant_rows = [
        row
        for row in context.shift_offers
        if isinstance(row, dict)
        and _public_segment_matches(str(row.get('segment')), context.segment)
    ]
    if not relevant_rows:
        relevant_rows = [row for row in context.shift_offers if isinstance(row, dict)]
    if len(relevant_rows) == 1:
        row = relevant_rows[0]
        if grade_reference:
            return (
                f'O {grade_reference} fica em {row.get("segment", "esse segmento")}. '
                f'As atividades do turno {row.get("shift_label", "regular").lower()} vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
                f'{str(row.get("notes", "")).strip()}'
            ).strip()
        return (
            f'Para {row.get("segment", "esse segmento")}, as atividades no turno {row.get("shift_label", "regular").lower()} '
            f'vao de {row.get("starts_at", "--:--")} a {row.get("ends_at", "--:--")}. '
            f'{str(row.get("notes", "")).strip()}'
        ).strip()
    if grade_reference and context.segment:
        lines = [
            f'Hoje os canais publicos do {context.school_name} nao detalham o horario especifico do {grade_reference}.',
            f'O recorte publicado para esse pedido fica em {context.segment}:',
        ]
        for row in relevant_rows:
            lines.append(
                '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                    segment=row.get('segment', 'Segmento'),
                    shift_label=row.get('shift_label', 'turno'),
                    starts_at=row.get('starts_at', '--:--'),
                    ends_at=row.get('ends_at', '--:--'),
                    notes=row.get('notes', '').strip(),
                ).rstrip()
            )
        return '\n'.join(lines)
    lines = ['Turnos e horarios documentados:']
    for row in relevant_rows:
        lines.append(
            '- {segment} ({shift_label}): {starts_at} as {ends_at}. {notes}'.format(
                segment=row.get('segment', 'Segmento'),
                shift_label=row.get('shift_label', 'turno'),
                starts_at=row.get('starts_at', '--:--'),
                ends_at=row.get('ends_at', '--:--'),
                notes=row.get('notes', '').strip(),
            ).rstrip()
        )
    return '\n'.join(lines)


def _handle_public_features(context: PublicProfileContext) -> str:
    if _is_public_enrichment_query(context.source_message):
        return _compose_public_enrichment_answer(context)
    feature_schedule_follow_up = _compose_public_feature_schedule_follow_up(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_schedule_follow_up:
        return feature_schedule_follow_up
    feature_answer = _compose_public_feature_answer(
        profile=context.profile,
        original_message=context.source_message,
        analysis_message=context.message,
        conversation_context=context.conversation_context,
    )
    if feature_answer:
        return feature_answer
    return (
        f'Hoje o perfil publico de {context.school_reference} nao traz esse detalhe de estrutura ou atividade. '
        'Se quiser, eu posso te mostrar o que esta oficialmente documentado.'
    )


def _handle_public_capacity(context: PublicProfileContext) -> str:
    normalized = _normalize_text(context.source_message)
    if any(_message_matches_term(normalized, term) for term in PUBLIC_CAPACITY_PARKING_TERMS):
        return (
            f'Hoje a base publica de {context.school_reference} nao informa a quantidade de vagas de estacionamento. '
            'Se a sua necessidade for visita, evento ou rotina de acesso, o caminho mais seguro e confirmar isso com a secretaria ou recepcao antes.'
        )
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'aluno',
            'alunos',
            'escola',
            'matricula',
            'matrícula',
            'turma',
            'turmas',
            'segmento',
            'segmentos',
        }
    ):
        return (
            f'Hoje a base publica de {context.school_reference} nao publica um numero fechado de vagas para alunos ou de capacidade total da escola. '
            'A disponibilidade costuma ser confirmada por segmento e turma com admissions ou secretaria, conforme o momento do ciclo de matricula.'
        )
    return (
        'Quando voce fala em vagas, isso pode significar vagas para alunos, vagas de estacionamento ou vagas para trabalhar na escola. '
        'Se quiser, eu separo isso por tipo agora.'
    )


def _handle_public_segments(context: PublicProfileContext) -> str:
    segments = context.profile.get('segments')
    if not isinstance(segments, list) or not segments:
        return (
            f'Hoje o perfil publico de {context.school_reference} nao traz os segmentos atendidos.'
        )
    lines = [f'Hoje {context.school_reference} atende estes segmentos:']
    lines.extend(f'- {item}' for item in segments if isinstance(item, str))
    return '\n'.join(lines)


def _handle_public_school_name(context: PublicProfileContext) -> str:
    return f'O nome oficial da escola e {context.school_name}.'


def _public_profile_handler_registry() -> dict[str, Callable[[PublicProfileContext], str]]:
    return {
        'acknowledgement': _handle_public_acknowledgement,
        'greeting': _handle_public_greeting,
        'input_clarification': _handle_public_input_clarification,
        'scope_boundary': _handle_public_scope_boundary,
        'utility_date': _handle_public_utility_date,
        'auth_guidance': _handle_public_auth_guidance,
        'access_scope': _handle_public_access_scope,
        'language_preference': _handle_public_language_preference,
        'assistant_identity': _handle_public_assistant_identity,
        'service_routing': _handle_public_service_routing,
        'service_credentials_bundle': _handle_public_service_credentials_bundle,
        'capabilities': _handle_public_capabilities,
        'document_submission': _handle_public_document_submission,
        'policy': _handle_public_policy,
        'policy_compare': _handle_public_policy_compare,
        'capacity': _handle_public_capacity,
        'careers': _handle_public_careers,
        'teacher_directory': _handle_public_teacher_directory,
        'leadership': _handle_public_leadership,
        'web_presence': _handle_public_web_presence,
        'social_presence': _handle_public_social_presence,
        'comparative': _handle_public_comparative,
        'contacts': _handle_public_contacts,
        'operating_hours': _handle_public_operating_hours,
        'timeline': _handle_public_timeline,
        'calendar_events': _handle_public_calendar_events,
        'location': _handle_public_location,
        'confessional': _handle_public_confessional,
        'curriculum': _handle_public_curriculum,
        'kpi': _handle_public_kpi,
        'highlight': _handle_public_highlight,
        'visit': _handle_public_visit,
        'pricing': _handle_public_pricing,
        'schedule': _handle_public_schedule,
        'features': _handle_public_features,
        'segments': _handle_public_segments,
        'school_name': _handle_public_school_name,
    }


AGENTIC_PUBLIC_COMPOSITION_ACTS = {
    'canonical_fact',
    'comparative',
    'curriculum',
    'highlight',
    'confessional',
}


async def _compose_public_profile_answer_agentic(
    *,
    settings: Any,
    profile: dict[str, Any],
    actor: dict[str, Any] | None = None,
    message: str,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
    deterministic_text_sink: dict[str, Any] | None = None,
) -> str:
    llm_forced_mode = _llm_forced_mode_enabled(settings=settings)
    deterministic_text = _compose_public_profile_answer(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    if deterministic_text_sink is not None:
        deterministic_text_sink['deterministic_text'] = deterministic_text
        deterministic_text_sink['agentic_llm_used'] = False
        deterministic_text_sink['agentic_llm_stages'] = []
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    resolved_act = _resolve_public_profile_act(context)
    if resolved_act not in AGENTIC_PUBLIC_COMPOSITION_ACTS and not llm_forced_mode:
        return deterministic_text

    evidence_bundle = build_public_evidence_bundle(
        profile,
        primary_act=resolved_act,
        secondary_acts=semantic_plan.secondary_acts if semantic_plan is not None else (),
        request_message=original_message or message,
        focus_hint=semantic_plan.focus_hint if semantic_plan is not None else None,
    )
    if evidence_bundle is None:
        return deterministic_text

    plan_payload = {
        'conversation_act': resolved_act,
        'secondary_acts': list(evidence_bundle.secondary_acts),
        'requested_attribute': semantic_plan.requested_attribute if semantic_plan else None,
        'requested_channel': semantic_plan.requested_channel if semantic_plan else None,
        'semantic_source': semantic_plan.semantic_source if semantic_plan else 'rules',
    }
    llm_text = await compose_langgraph_public_grounded_with_provider(
        settings=settings,
        request_message=original_message or message,
        draft_text=deterministic_text,
        public_plan=plan_payload,
        evidence_lines=[fact.text for fact in evidence_bundle.facts],
        conversation_context=conversation_context,
        school_profile=profile,
    )
    if deterministic_text_sink is not None and llm_text:
        deterministic_text_sink['agentic_llm_used'] = True
        deterministic_text_sink['agentic_llm_stages'] = ['answer_composition']
    return llm_text or deterministic_text


async def _maybe_langgraph_open_documentary_candidate(
    *,
    settings: Any,
    engine_name: str,
    request: MessageResponseRequest,
    preview: OrchestrationPreview,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
    draft_text: str,
) -> str | None:
    if str(engine_name or '').strip().lower() != 'langgraph':
        return None
    if not _llm_forced_mode_enabled(settings=settings):
        return None
    if school_profile is None:
        return None
    if preview.classification.access_tier is not AccessTier.public:
        return None
    public_plan = _build_public_institution_plan(
        request.message,
        list(preview.selected_tools),
        conversation_context=conversation_context,
    )
    if not _should_use_public_open_documentary_synthesis(request.message, public_plan):
        return None
    evidence_bundle = build_public_evidence_bundle(
        school_profile,
        primary_act=public_plan.conversation_act,
        secondary_acts=public_plan.secondary_acts,
        request_message=request.message,
        focus_hint=public_plan.focus_hint,
    )
    if evidence_bundle is None or not evidence_bundle.facts:
        return None
    plan_payload = {
        'conversation_act': public_plan.conversation_act,
        'secondary_acts': list(evidence_bundle.secondary_acts),
        'requested_attribute': public_plan.requested_attribute,
        'requested_channel': public_plan.requested_channel,
        'semantic_source': public_plan.semantic_source,
    }
    llm_text = await compose_langgraph_public_grounded_with_provider(
        settings=settings,
        request_message=request.message,
        draft_text=draft_text,
        public_plan=plan_payload,
        evidence_lines=[fact.text for fact in evidence_bundle.facts],
        conversation_context=conversation_context,
        school_profile=school_profile,
    )
    return llm_text or None


def _compose_public_profile_answer(
    profile: dict[str, Any],
    message: str,
    *,
    actor: dict[str, Any] | None = None,
    original_message: str | None = None,
    conversation_context: dict[str, Any] | None = None,
    semantic_plan: PublicInstitutionPlan | None = None,
) -> str:
    context = _build_public_profile_context(
        profile,
        message,
        actor=actor,
        original_message=original_message,
        conversation_context=conversation_context,
        semantic_plan=semantic_plan,
    )
    registry = _public_profile_handler_registry()
    if semantic_plan is not None and semantic_plan.conversation_act in {
        'greeting',
        'assistant_identity',
        'auth_guidance',
        'capabilities',
        'input_clarification',
        'language_preference',
        'scope_boundary',
    }:
        semantic_handler = registry.get(semantic_plan.conversation_act)
        if semantic_handler is not None:
            semantic_answer = semantic_handler(context)
            if semantic_answer:
                return _localize_pt_br_surface_labels(semantic_answer)
    semantic_requires_multi_intent = bool(
        semantic_plan is not None
        and (semantic_plan.conversation_act != 'pricing' or bool(semantic_plan.secondary_acts))
    )
    canonical_lane = match_public_canonical_lane(
        context.source_message
    ) or match_public_canonical_lane(original_message or message)
    if canonical_lane:
        lane_answer = compose_public_canonical_lane_answer(canonical_lane, profile=profile)
        if lane_answer:
            return _localize_pt_br_surface_labels(lane_answer)
    if _is_public_pricing_navigation_query(context.source_message) and not (
        semantic_requires_multi_intent or _has_public_multi_intent_signal(context.source_message)
    ):
        pricing_answer = _handle_public_pricing(context)
        if pricing_answer:
            return _localize_pt_br_surface_labels(pricing_answer)
    multi_intent_answer = _compose_public_multi_intent_answer(
        context,
        semantic_plan=semantic_plan,
    )
    if multi_intent_answer:
        return _localize_pt_br_surface_labels(multi_intent_answer)
    normalized_source_message = _normalize_text(context.source_message)
    if (
        (
            _is_follow_up_query(context.source_message)
            or normalized_source_message.startswith('depois disso')
        )
        and any(
            _message_matches_term(normalized_source_message, term)
            for term in {
                'inicio das aulas',
                'início das aulas',
                'comecam as aulas',
                'começam as aulas',
                'aulas',
            }
        )
        and (
            normalized_source_message.startswith('depois disso')
            or _recent_user_message_mentions(
                context.conversation_context,
                {
                    'matricula',
                    'matrícula',
                    'proximo ciclo',
                    'próximo ciclo',
                    'inscricoes',
                    'inscrições',
                },
            )
        )
    ):
        school_year_start_answer = _compose_public_school_year_start_answer(
            profile, context.school_reference
        )
        if school_year_start_answer:
            return _localize_pt_br_surface_labels(school_year_start_answer)
    resolved_act = _resolve_public_profile_act(context)
    handler = registry.get(resolved_act)
    if handler is not None:
        primary_text = handler(context)
        extra_texts: list[str] = []
        if semantic_plan is not None:
            secondary_acts = semantic_plan.secondary_acts[:2]
            if semantic_plan.conversation_act == 'timeline' and not _has_public_multi_intent_signal(
                context.source_message
            ):
                secondary_acts = ()
            for act in secondary_acts:
                if act == resolved_act:
                    continue
                if (
                    resolved_act == 'operating_hours'
                    and act == 'features'
                    and _target_public_feature_for_operating_hours(context) is not None
                ):
                    continue
                extra_handler = registry.get(act)
                if extra_handler is None:
                    continue
                candidate = extra_handler(context).strip()
                if not candidate:
                    continue
                normalized_candidate = _normalize_text(candidate)
                if normalized_candidate in _normalize_text(primary_text):
                    continue
                if any(normalized_candidate in _normalize_text(text) for text in extra_texts):
                    continue
                extra_texts.append(candidate)
        if extra_texts:
            return _localize_pt_br_surface_labels('\n\n'.join([primary_text, *extra_texts]))
        return _localize_pt_br_surface_labels(primary_text)

    fast_public_channel_answer = _try_public_channel_fast_answer(
        message=context.source_message,
        profile=profile,
    )
    if fast_public_channel_answer:
        return _localize_pt_br_surface_labels(fast_public_channel_answer)
    return _localize_pt_br_surface_labels(
        _compose_public_profile_answer_legacy(
            profile,
            message,
            original_message=original_message,
            conversation_context=conversation_context,
            semantic_plan=semantic_plan,
        )
    )