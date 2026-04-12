from __future__ import annotations

import re
import unicodedata

from .public_doc_knowledge import match_public_canonical_lane

_DIRECT_ADMIN_STATUS_TERMS = {
    'dados cadastrais',
    'meus dados cadastrais',
    'situacao administrativa',
    'status administrativo',
    'status documental',
    'pendencia documental',
    'pendencias documentais',
    'pendencia administrativa',
    'pendencias administrativas',
    'documentacao administrativa',
    'documentacao do cadastro',
    'cadastro desatualizado',
    'cadastro incompleto',
}

_ADMIN_ATTRIBUTE_TERMS = {
    'documentacao',
    'documentos',
    'documental',
    'cadastro',
    'email',
    'telefone',
    'comprovante',
    'residencia',
    'residencial',
    'pendencia',
    'pendencias',
    'regularizar',
    'bloqueando atendimento',
    'bloqueio',
}

_ADMIN_FOLLOW_UP_TERMS = {
    'proximo passo',
    'qual o proximo passo',
    'o que falta',
    'agir em seguida',
    'como agir em seguida',
    'o que fazer em seguida',
}

_PERSONAL_ADMIN_ANCHORS = {
    'meu',
    'minha',
    'meus',
    'minhas',
    'responsavel',
    'familia',
    'familias',
    'cadastro',
    'documentacao',
    'administrativo',
    'administrativa',
}

_PUBLIC_INSTITUTION_OVERRIDES = {
    'matricula',
    'rematricula',
    'transferencia',
    'cancelamento',
    'visita',
    'site',
    'instagram',
    'endereco',
    'horario',
    'calendario',
    'politica da escola',
    'politica do colegio',
    'protocolo da escola',
}

_SCHOOL_DOMAIN_TERMS = {
    'escola',
    'colegio',
    'eduassist',
    'matricula',
    'mensalidade',
    'biblioteca',
    'visita',
    'secretaria',
    'financeiro',
    'fatura',
    'boleto',
    'nota',
    'notas',
    'falta',
    'faltas',
    'aluno',
    'aluna',
    'estudante',
    'professor',
    'professora',
    'turno',
    'turma',
    'turmas',
    'disciplina',
    'disciplinas',
    'materia',
    'materias',
    'projeto de vida',
    'aprovacao',
    'recuperacao',
    'calendario',
    'portal',
    'coordenacao',
    'coordenador',
    'direcao',
    'diretor',
    'diretora',
    'uniforme',
    'transporte',
    'admissions',
    'maconha',
    'droga',
    'drogas',
    'fumar',
    'vape',
    'cigarro',
    'alcool',
    'álcool',
    'conduta',
    'comportamento',
    'bullying',
}


def normalize_guardrail_text(text: str) -> str:
    lowered = unicodedata.normalize('NFKD', str(text or '')).encode('ascii', 'ignore').decode('ascii').lower()
    return re.sub(r'\s+', ' ', lowered).strip()


def looks_like_public_canonical_request(message: str) -> bool:
    return match_public_canonical_lane(message) is not None


def looks_like_school_domain_request(message: str) -> bool:
    if looks_like_public_canonical_request(message):
        return True
    normalized = normalize_guardrail_text(message)
    if not normalized:
        return False
    return any(term in normalized for term in _SCHOOL_DOMAIN_TERMS)


def looks_like_explicit_admin_status_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    if looks_like_public_canonical_request(message):
        return False
    normalized = normalize_guardrail_text(message)
    if not normalized:
        return False
    if any(term in normalized for term in _DIRECT_ADMIN_STATUS_TERMS):
        return True
    personal_anchor = any(term in normalized for term in _PERSONAL_ADMIN_ANCHORS)
    if any(term in normalized for term in _PUBLIC_INSTITUTION_OVERRIDES) and not personal_anchor:
        return False
    if personal_anchor and any(term in normalized for term in _ADMIN_ATTRIBUTE_TERMS):
        return True
    if any(term in normalized for term in _ADMIN_FOLLOW_UP_TERMS) and any(
        term in normalized for term in {'cadastro', 'documentacao', 'documentos', 'administrativo', 'responsavel'}
    ):
        return True
    return False
