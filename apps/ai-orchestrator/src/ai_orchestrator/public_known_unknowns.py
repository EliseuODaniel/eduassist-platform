from __future__ import annotations

from dataclasses import dataclass

import re
import unicodedata


@dataclass(frozen=True)
class PublicKnownUnknownRule:
    key: str
    triggers: tuple[str, ...]
    required_terms: tuple[str, ...] = ()


_RULES: tuple[PublicKnownUnknownRule, ...] = (
    PublicKnownUnknownRule(
        key='total_students',
        triggers=(
            'quantos alunos',
            'quantidade de alunos',
            'quantidade total de alunos',
            'numero de alunos',
            'número de alunos',
            'numero total de alunos',
            'número total de alunos',
            'total de alunos',
        ),
    ),
    PublicKnownUnknownRule(
        key='total_teachers',
        triggers=(
            'quantos professores',
            'quantidade de professores',
            'quantidade total de professores',
            'quantidade publica de professores',
            'quantidade pública de professores',
            'numero de professores',
            'número de professores',
            'numero publico de professores',
            'número público de professores',
            'numero total de professores',
            'número total de professores',
            'total de professores',
        ),
    ),
    PublicKnownUnknownRule(
        key='classroom_count',
        triggers=(
            'quantas salas',
            'quantidade de salas',
            'quantidade total de salas',
            'numero de salas',
            'número de salas',
            'numero total de salas',
            'número total de salas',
            'total de salas',
        ),
    ),
    PublicKnownUnknownRule(
        key='library_book_count',
        triggers=(
            'quantos livros',
            'quantidade de livros',
            'quantidade total de livros',
            'numero de livros',
            'número de livros',
            'numero total de livros',
            'número total de livros',
            'total de livros',
        ),
        required_terms=('biblioteca', 'livros', 'acervo'),
    ),
    PublicKnownUnknownRule(
        key='minimum_age',
        triggers=('idade minima', 'idade mínima', 'idade para estudar', 'idade para matricular'),
    ),
    PublicKnownUnknownRule(
        key='cafeteria_menu',
        triggers=('cardapio', 'cardápio'),
        required_terms=('cantina',),
    ),
)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r'\s+', ' ', text.lower()).strip()
    return text


def _matches_term(normalized_message: str, term: str) -> bool:
    escaped = re.escape(_normalize_text(term))
    pattern = r'(?<!\w)' + escaped.replace(r'\ ', r'\s+') + r'(?!\w)'
    return re.search(pattern, normalized_message) is not None


def detect_public_known_unknown_key(message: str) -> str | None:
    normalized_message = _normalize_text(message)
    for rule in _RULES:
        if not any(_matches_term(normalized_message, term) for term in rule.triggers):
            continue
        if rule.required_terms and not any(_matches_term(normalized_message, term) for term in rule.required_terms):
            continue
        return rule.key
    return None


def compose_public_known_unknown_answer(
    *,
    key: str,
    school_name: str = 'Colegio Horizonte',
) -> str | None:
    school_reference = str(school_name or 'Colegio Horizonte').strip() or 'Colegio Horizonte'
    if key == 'total_students':
        return (
            f'Hoje os canais publicos de {school_reference} nao informam o total de alunos matriculados. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if key == 'total_teachers':
        return (
            f'Hoje os canais publicos de {school_reference} nao informam a quantidade total de professores. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if key == 'classroom_count':
        return (
            f'Hoje os canais publicos de {school_reference} nao informam a quantidade total de salas de aula. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if key == 'library_book_count':
        return (
            f'Hoje os canais publicos de {school_reference} nao informam a quantidade total de livros da biblioteca. '
            'Entao a pergunta e valida, mas esse dado nao esta publicado oficialmente.'
        )
    if key == 'minimum_age':
        return (
            f'Hoje os canais publicos de {school_reference} nao publicam uma idade minima exata para ingresso. '
            'O que aparece oficialmente sao os segmentos atendidos e o enquadramento por serie; para confirmar idade e adequacao de ingresso, o canal certo e matricula e atendimento comercial.'
        )
    if key == 'cafeteria_menu':
        return (
            f'Hoje os canais publicos de {school_reference} confirmam que ha cantina e almoco supervisionado, '
            'mas nao publicam um cardapio detalhado. Para esse detalhe, o melhor caminho e a secretaria ou o canal comercial.'
        )
    return None


def resolve_public_known_unknown_answer(
    message: str,
    *,
    school_name: str = 'Colegio Horizonte',
) -> str | None:
    key = detect_public_known_unknown_key(message)
    if not key:
        return None
    return compose_public_known_unknown_answer(key=key, school_name=school_name)
