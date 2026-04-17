from __future__ import annotations

import re
from typing import Any

from .conversation_focus_runtime import _normalize_text
from .intent_analysis_runtime import _message_matches_term


def _compose_public_pedagogical_answer(profile: dict[str, Any], message: str) -> str | None:
    from .public_profile_runtime import _compose_public_pedagogical_answer as _impl

    return _impl(profile, message)


def _requested_unpublished_public_segment(context: Any) -> str | None:
    from .public_profile_runtime import _requested_unpublished_public_segment as _impl

    return _impl(context)


def _compose_public_segment_scope_gap(
    context: Any,
    *,
    requested_segment: str,
    topic: str,
) -> str:
    from .public_profile_runtime import _compose_public_segment_scope_gap as _impl

    return _impl(context, requested_segment=requested_segment, topic=topic)


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
    from .public_profile_runtime import (
        ACADEMIC_DIFFICULTY_TERMS,
        PUBLIC_CURRICULUM_SCOPE_TERMS,
        PUBLIC_CURRICULUM_TERMS,
        PUBLIC_PEDAGOGICAL_TERMS,
    )

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


def _match_public_curriculum_component(
    components: tuple[str, ...],
    requested_subject: str,
) -> str | None:
    from .public_profile_runtime import SUBJECT_HINTS

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


def _handle_public_curriculum(context: Any) -> str:
    from .public_profile_runtime import ACADEMIC_DIFFICULTY_TERMS, PUBLIC_CURRICULUM_SCOPE_TERMS

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
    if requested_subject == '__list__' and context.curriculum_components:
        components = ', '.join(context.curriculum_components[:10])
        extra = ' e outras frentes eletivas' if len(context.curriculum_components) > 10 else ''
        return f'Pelo perfil publico atual de {context.school_reference}, as materias que aparecem com mais clareza sao {components}{extra}.'
    if any(_message_matches_term(context.normalized, term) for term in ACADEMIC_DIFFICULTY_TERMS) and any(
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
