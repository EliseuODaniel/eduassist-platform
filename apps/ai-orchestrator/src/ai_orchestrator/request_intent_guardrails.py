from __future__ import annotations

import re
import unicodedata

from eduassist_semantic_ingress import (
    looks_like_high_confidence_public_school_faq as _shared_high_confidence_public_school_faq,
)

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


def looks_like_high_confidence_public_school_faq(
    message: str,
    *,
    conversation_context: dict | None = None,
    school_profile: dict | None = None,
) -> bool:
    if _shared_high_confidence_public_school_faq(message):
        return True
    if looks_like_public_canonical_request(message):
        return True
    normalized = normalize_guardrail_text(message)
    if not normalized:
        return False
    enrollment_documents_terms = {
        'quais documentos preciso',
        'documentos exigidos',
        'documentos sao exigidos',
        'documentos são exigidos',
        'documentos necessarios',
        'documentos necessários',
        'preciso para matricula',
        'preciso para a matricula',
        'preciso para matrícula',
        'preciso para a matrícula',
    }
    if 'matricula' in normalized and any(term in normalized for term in enrollment_documents_terms):
        return True
    if any(
        term in normalized
        for term in {
            'quando iniciam as aulas',
            'quando comecam as aulas',
            'quando começa as aulas',
            'quando começam as aulas',
            'inicio das aulas',
            'início das aulas',
            'ano letivo',
        }
    ):
        return True
    if 'biblioteca' in normalized and any(
        term in normalized for term in {'tem biblioteca', 'horario', 'horário', 'abre', 'fecha', 'funciona'}
    ):
        return True
    if any(
        term in normalized
        for term in {
            'que horas comeca a aula',
            'que horas começa a aula',
            'horario da manha',
            'horário da manhã',
            'turno da manha',
            'turno da manhã',
            'aula de manha',
            'aula de manhã',
            'aula da manha',
            'aula da manhã',
            'tem aula de manha',
            'tem aula de manhã',
            'qual horario da aula',
            'qual horário da aula',
        }
    ):
        return True
    if any(term in normalized for term in {'manha', 'manhã', 'matutino', 'matutina'}) and any(
        term in normalized for term in {'aula', 'turno', 'turma', 'horario', 'horário', 'comeca', 'começa', 'inicio', 'início'}
    ):
        return True
    if any(
        term in normalized for term in {'diretor', 'diretora', 'direcao', 'direção', 'diretoria'}
    ) and any(
        term in normalized
        for term in {'contato', 'telefone', 'email', 'e-mail', 'whatsapp', 'como falar'}
    ):
        return True
    return False


def looks_like_school_domain_request(message: str) -> bool:
    if looks_like_high_confidence_public_school_faq(message):
        return True
    normalized = normalize_guardrail_text(message)
    if not normalized:
        return False
    return any(term in normalized for term in _SCHOOL_DOMAIN_TERMS)


def looks_like_explicit_admin_status_query(message: str, *, authenticated: bool) -> bool:
    if not authenticated:
        return False
    if looks_like_high_confidence_public_school_faq(message):
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
