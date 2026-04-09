from __future__ import annotations

import re
import unicodedata

from pydantic import BaseModel, Field


_PROTOCOL_CODE_PATTERN = re.compile(r'\b(?:VIS|REQ|ATD)-\d{4}-\d{3,}\b', re.IGNORECASE)
_QUANTITY_PATTERN = re.compile(r'\b(\d{1,3})\s+(?:filho|filhos|dependente|dependentes)\b', re.IGNORECASE)
_HYPOTHETICAL_MARKERS = (
    'se eu tiver',
    'se eu tivesse',
    'se eu matricular',
    'se eu matriculasse',
    'se eu inscrever',
    'se eu inscrevesse',
    'se eu colocar',
    'se eu colocasse',
    'hipoteticamente',
    'num cenario hipotetico',
    'num cenário hipotético',
    'quanto daria',
    'quanto dariam',
    'quanto ficaria',
    'quanto ficariam',
    'quanto seria',
    'quanto seriam',
)
_PUBLIC_PRICE_MARKERS = (
    'mensalidade',
    'mensalidades',
    'matricula',
    'matrícula',
    'matricular',
    'matricular meus',
    'inscrever',
    'inscrever meus',
    'colocar meus filhos',
    'desconto',
    'bolsa',
    'valor',
    'quanto vou pagar',
    'quanto eu pagaria',
)
_ADMIN_TERMS = (
    'cadastro',
    'dados cadastrais',
    'alterar meu cadastro',
    'altero meu cadastro',
    'meu acesso',
)
_LOCATION_TERMS = (
    'endereco',
    'endereço',
    'bairro',
    'qual bairro',
    'em qual bairro',
    'onde fica',
    'estado fica',
    'cidade fica',
    'cep',
)


def _normalize_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r'[^a-z0-9\s/-]+', ' ', text.lower())
    return ' '.join(text.split())


class ResolvedEntityHints(BaseModel):
    protocol_code: str | None = None
    quantity_hint: int | None = None
    is_hypothetical: bool = False
    domain_hint: str | None = None
    requested_attribute: str | None = None
    focus_hint: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


def resolve_entity_hints(message: str) -> ResolvedEntityHints:
    normalized = _normalize_text(message)
    protocol_match = _PROTOCOL_CODE_PATTERN.search(message or '')
    quantity_match = _QUANTITY_PATTERN.search(message or '')
    quantity_hint = int(quantity_match.group(1)) if quantity_match else None
    is_hypothetical = any(marker in normalized for marker in _HYPOTHETICAL_MARKERS)

    domain_hint: str | None = None
    requested_attribute: str | None = None
    focus_hint: str | None = None
    confidence = 0.25

    if protocol_match:
        domain_hint = 'workflow'
        requested_attribute = 'protocol_status'
        focus_hint = protocol_match.group(0).upper()
        confidence = 0.92
    elif quantity_hint is not None and is_hypothetical and any(term in normalized for term in _PUBLIC_PRICE_MARKERS):
        domain_hint = 'public_pricing'
        requested_attribute = 'aggregate_price'
        focus_hint = 'hypothetical_family_pricing'
        confidence = 0.9
    elif any(term in normalized for term in _ADMIN_TERMS):
        domain_hint = 'admin'
        requested_attribute = 'account_or_registry'
        focus_hint = 'authenticated_account'
        confidence = 0.78
    elif any(term in normalized for term in _LOCATION_TERMS):
        domain_hint = 'public_profile'
        requested_attribute = 'location'
        focus_hint = 'institution_location'
        confidence = 0.7

    return ResolvedEntityHints(
        protocol_code=protocol_match.group(0).upper() if protocol_match else None,
        quantity_hint=quantity_hint,
        is_hypothetical=is_hypothetical,
        domain_hint=domain_hint,
        requested_attribute=requested_attribute,
        focus_hint=focus_hint,
        confidence=confidence,
    )
