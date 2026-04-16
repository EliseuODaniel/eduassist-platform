from __future__ import annotations

import re
from typing import Any


_INTERNAL_DOC_STOPWORDS = {
    'manual',
    'interno',
    'interna',
    'documento',
    'documentos',
    'protocolo',
    'politica',
    'guia',
    'sobre',
    'para',
    'com',
    'por',
    'uma',
    'umas',
    'uns',
    'das',
    'dos',
    'que',
    'escopo',
    'parcial',
    'colegio',
    'colegio horizonte',
    'horizonte',
}

_INTERNAL_DOC_GENERIC_TERMS = {
    'manual',
    'interno',
    'interna',
    'material',
    'orientacao',
    'orientação',
    'procedimento',
    'protocolo',
    'politica',
    'politicas',
    'guia',
    'fluxo',
    'regras',
    'processo',
    'processos',
    'rotina',
    'validacao',
    'validacoes',
    'responsaveis',
    'alunos',
    'familias',
    'escola',
}

_INTERNAL_DOC_RARE_TERMS = {
    'telegram',
    'escopo',
    'parcial',
    'negociacao',
    'negociação',
    'quitacao',
    'quitação',
    'promessa',
    'validacao',
    'validação',
    'validacoes',
    'validações',
    'rotina',
    'professor',
    'docente',
    'hospedagem',
    'internacional',
    'playbook',
    'excursao',
    'excursão',
}


def _normalize_text(value: str) -> str:
    return re.sub(r'\s+', ' ', str(value or '').lower()).strip()


def _looks_like_internal_document_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if not normalized:
        return False
    if any(
        term in normalized
        for term in {
            'documentos publicos',
            'documentos públicos',
            'documentacao publica',
            'documentação pública',
            'material publico',
            'material público',
            'base publica',
            'base pública',
            'pelos documentos publicos',
            'pelos documentos públicos',
        }
    ):
        return False
    anchor = any(
        term in normalized
        for term in {
            'manual interno',
            'protocolo interno',
            'playbook interno',
            'documento interno',
            'material interno',
            'orientacao interna',
            'orientação interna',
            'procedimento interno',
            'rotina interna',
            'validacao interna',
            'validação interna',
            'validacoes internas',
            'validações internas',
        }
    )
    if anchor:
        return True
    doc_nouns = sum(
        1
        for term in {
            'manual',
            'protocolo',
            'playbook',
            'documento',
            'material',
            'orientacao',
            'orientação',
            'procedimento',
            'rotina',
            'validacao',
            'validação',
            'validacoes',
            'validações',
        }
        if term in normalized
    )
    rare_terms = sum(1 for term in _INTERNAL_DOC_RARE_TERMS if term in normalized)
    return doc_nouns >= 1 and rare_terms >= 1


def _internal_doc_query_tokens(message: str) -> list[str]:
    tokens = re.findall(r'[a-z0-9]+', _normalize_text(message))
    return [token for token in tokens if len(token) >= 4 and token not in _INTERNAL_DOC_STOPWORDS]


def _internal_doc_anchor_terms(message: str) -> set[str]:
    return {
        token
        for token in _internal_doc_query_tokens(message)
        if token not in _INTERNAL_DOC_GENERIC_TERMS
    }


def _internal_doc_rare_terms(message: str) -> set[str]:
    return {
        token
        for token in _internal_doc_query_tokens(message)
        if any(token.startswith(marker) or marker.startswith(token) for marker in _INTERNAL_DOC_RARE_TERMS)
    }


def _internal_doc_hit_score(query: str, hit: dict[str, Any]) -> float:
    query_terms = set(_internal_doc_query_tokens(query))
    if not query_terms:
        return 0.0
    title = _normalize_text(str(hit.get('title') or hit.get('document_title') or ''))
    summary = _normalize_text(
        str(
            hit.get('summary')
            or hit.get('contextual_summary')
            or hit.get('text_excerpt')
            or ''
        )
    )
    content = _normalize_text(
        str(
            hit.get('content')
            or hit.get('text_content')
            or hit.get('excerpt')
            or ''
        )
    )
    title_terms = {token for token in re.findall(r'[a-z0-9]+', title) if len(token) >= 4 and token not in _INTERNAL_DOC_STOPWORDS}
    anchor_terms = _internal_doc_anchor_terms(query)
    rare_terms = _internal_doc_rare_terms(query)

    score = 0.0
    score += len(query_terms & title_terms) * 3.0
    score += sum(1.0 for term in query_terms if term in summary)
    score += sum(0.5 for term in query_terms if term in content)
    score += len(anchor_terms & title_terms) * 2.0
    score += sum(2.0 for term in rare_terms if term in title or term in summary)
    if any(term in title for term in {'manual interno', 'protocolo interno', 'playbook interno'}):
        score += 1.5
    return score
