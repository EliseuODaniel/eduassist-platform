from __future__ import annotations

from typing import Any

from .public_act_rules_runtime import (
    _is_leadership_specific_query,
    _matches_public_location_rule,
)
from .public_contact_runtime import (
    _contact_is_general_school_query,
    _contact_value,
    _format_contact_origin,
    _requested_public_attribute,
    _select_primary_contact_entry,
    _wants_contact_list,
)
from .public_organization_runtime import _compose_public_leadership_answer
from .public_profile_support_runtime import _school_object_reference


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _handle_public_contacts_impl(context: Any) -> str:
    if _is_leadership_specific_query(context.source_message):
        return _compose_public_leadership_answer(
            context.profile,
            context.source_message,
            requested_attribute_override=_requested_public_attribute(
                context.contact_reference_message
            )
            or 'contact',
        )
    wants_location = _matches_public_location_rule(context.source_message)
    wants_secretaria_guidance = any(
        _message_matches_term(context.normalized, term)
        for term in {'secretaria', 'secretaria escolar', 'atendimento da secretaria'}
    )
    wants_finance_guidance = any(
        _message_matches_term(context.normalized, term)
        for term in {'financeiro', 'tesouraria', 'cobranca', 'cobrança', 'mensalidade', 'boleto'}
    )
    if wants_location or wants_secretaria_guidance:
        lines: list[str] = []
        if wants_location:
            location = ', '.join(
                part
                for part in [context.address_line, context.district, context.city, context.state]
                if part
            )
            if context.postal_code:
                location = f'{location}, CEP {context.postal_code}'
            if location:
                lines.append(
                    f'O endereco publicado de {context.school_reference} hoje e {location}.'
                )
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=['Secretaria'],
        )
        if primary_phone:
            lines.append(f'O telefone principal hoje e {primary_phone.get("value")}.')
        if wants_secretaria_guidance:
            secretaria_whatsapp = _select_primary_contact_entry(
                context.profile,
                'whatsapp',
                context.contact_reference_message,
                preferred_labels=['Secretaria digital', 'Atendimento comercial'],
            )
            secretaria_email = _select_primary_contact_entry(
                context.profile,
                'email',
                context.contact_reference_message,
                preferred_labels=['Secretaria'],
            )
            if secretaria_whatsapp:
                lines.append(
                    f'O canal mais direto para falar com a secretaria hoje e o WhatsApp {secretaria_whatsapp.get("value")}.'
                )
            elif secretaria_email:
                lines.append(
                    f'O canal mais direto para a secretaria hoje e o email {secretaria_email.get("value")}.'
                )
        if wants_finance_guidance:
            finance_phone = _select_primary_contact_entry(
                context.profile,
                'telefone',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            finance_whatsapp = _select_primary_contact_entry(
                context.profile,
                'whatsapp',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            finance_email = _select_primary_contact_entry(
                context.profile,
                'email',
                context.contact_reference_message,
                preferred_labels=['Financeiro'],
            )
            if finance_whatsapp:
                lines.append(
                    f'O canal mais direto do financeiro hoje e o WhatsApp {finance_whatsapp.get("value")}.'
                )
            elif finance_email:
                lines.append(
                    f'O canal mais direto do financeiro hoje e o email {finance_email.get("value")}.'
                )
            elif finance_phone:
                lines.append(
                    f'O telefone mais direto do financeiro hoje e {finance_phone.get("value")}.'
                )
        if lines:
            return ' '.join(lines)

    phone_lines = _contact_value(context.profile, 'telefone')
    whatsapp_lines = _contact_value(context.profile, 'whatsapp')
    email_lines = _contact_value(context.profile, 'email')
    if _message_matches_term(context.normalized, 'caixa postal'):
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional. '
                f'Se precisar de contato, o telefone principal e {primary_phone.get("value")}.'
            )
        return f'Hoje {context.school_reference} nao trabalha com caixa postal como canal institucional.'
    fax_only_query = _message_matches_term(context.normalized, 'fax') and not any(
        _message_matches_term(context.normalized, term)
        for term in {'telefone', 'fone', 'ligar', 'ligo', 'whatsapp', 'email'}
    )
    if fax_only_query:
        if context.fax_number:
            return f'O fax institucional publicado de {context.school_reference} hoje e {context.fax_number}.'
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone:
            return (
                f'Hoje {context.school_reference} nao publica numero de fax. '
                f'Se quiser ligar, o telefone principal e {primary_phone.get("value")}.'
            )
        return f'Hoje {context.school_reference} nao publica numero de fax.'
    if context.requested_channel == 'telefone':
        primary_phone = _select_primary_contact_entry(
            context.profile,
            'telefone',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_phone and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_phone.get('label')
            value = primary_phone.get('value')
            if label:
                response = (
                    f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "telefone")}.'
                )
            else:
                response = f'O telefone principal {_school_object_reference(context.school_reference)} hoje e {value}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += (
                    f' O fax publicado e {context.fax_number}.'
                    if context.fax_number
                    else ' Hoje a escola nao publica numero de fax.'
                )
            return response
        if len(phone_lines) == 1:
            response = f'O telefone oficial de {context.school_reference} e {phone_lines[0]}.'
            if _message_matches_term(context.normalized, 'fax'):
                response += ' Hoje a escola nao publica numero de fax.'
            return response
        lines = [f'Os telefones oficiais de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in phone_lines)
        if _message_matches_term(context.normalized, 'fax'):
            lines.append('- Fax: nao publicado')
        return '\n'.join(lines)
    if context.requested_channel == 'whatsapp':
        primary_whatsapp = _select_primary_contact_entry(
            context.profile,
            'whatsapp',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_whatsapp and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_whatsapp.get('label')
            value = primary_whatsapp.get('value')
            if label:
                return (
                    f'O WhatsApp mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "whatsapp")}.'
                )
            return f'O WhatsApp oficial {_school_object_reference(context.school_reference)} hoje e {value}.'
        if len(whatsapp_lines) == 1:
            return f'O WhatsApp oficial de {context.school_reference} hoje e {whatsapp_lines[0]}.'
        lines = [f'Os canais de WhatsApp publicados por {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in whatsapp_lines)
        return '\n'.join(lines)
    if context.requested_channel == 'email':
        primary_email = _select_primary_contact_entry(
            context.profile,
            'email',
            context.contact_reference_message,
            preferred_labels=context.preferred_contact_labels,
        )
        if primary_email and (
            _contact_is_general_school_query(context.contact_reference_message)
            or not _wants_contact_list(context.contact_reference_message)
        ):
            label = primary_email.get('label')
            value = primary_email.get('value')
            if label:
                return (
                    f'O email mais direto {_school_object_reference(context.school_reference)} hoje e {value}, '
                    f'{_format_contact_origin(label, "email")}.'
                )
            return f'O email institucional publicado de {context.school_reference} e {value}.'
        if len(email_lines) == 1:
            return (
                f'O email institucional publicado de {context.school_reference} e {email_lines[0]}.'
            )
        lines = [f'Os emails institucionais publicados de {context.school_reference} hoje sao:']
        lines.extend(f'- {item}' for item in email_lines)
        return '\n'.join(lines)
    lines = [f'Voce pode falar com {context.school_reference} por estes canais oficiais:']
    lines.extend(f'- {item}' for item in [*phone_lines, *whatsapp_lines, *email_lines])
    if _message_matches_term(context.normalized, 'fax'):
        lines.append('- Fax: nao publicado')
    return '\n'.join(lines)
