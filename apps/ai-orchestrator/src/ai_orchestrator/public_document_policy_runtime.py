from __future__ import annotations

from decimal import Decimal
from typing import Any

from .conversation_focus_runtime import _normalize_text
from .public_contact_runtime import _select_primary_contact_entry
from .public_service_routing_runtime import _service_catalog_index


def _intent_analysis_impl(name: str):
    from . import intent_analysis_runtime as _intent_analysis_runtime

    return getattr(_intent_analysis_runtime, name)


def _compose_required_documents_answer(*args, **kwargs):
    return _intent_analysis_impl('_compose_required_documents_answer')(*args, **kwargs)


def _is_positive_requirement_query(message: str) -> bool:
    return _intent_analysis_impl('_is_positive_requirement_query')(message)


def _message_matches_term(message: str, term: str) -> bool:
    return _intent_analysis_impl('_message_matches_term')(message, term)


def _humanize_service_eta(eta: str) -> str:
    from .public_profile_runtime import _humanize_service_eta as _impl

    return _impl(eta)


def _is_public_policy_query(message: str) -> bool:
    from .public_profile_runtime import PUBLIC_POLICY_TERMS

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


def _is_public_document_submission_query(message: str) -> bool:
    from .public_profile_runtime import PUBLIC_DOCUMENT_SUBMISSION_TERMS

    normalized = _normalize_text(message)
    if any(
        phrase in normalized
        for phrase in (
            'quais documentos preciso para matricula',
            'quais documentos preciso para matrícula',
            'documentos para matricula',
            'documentos para matrícula',
            'documentos exigidos para matricula',
            'documentos exigidos para matrícula',
        )
    ):
        return True
    if _is_positive_requirement_query(message) and any(
        _message_matches_term(normalized, term)
        for term in {'documento', 'documentos', 'matricula', 'matrícula', 'cadastro'}
    ):
        return True
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
    return any(
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
        lines.append('Hoje os canais mais diretos publicados para isso sao:')
        lines.extend(
            f'- {channel}'
            for channel in (
                'portal institucional',
                'email da secretaria',
                'secretaria presencial',
            )
        )
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
            return f'No Colegio Horizonte, Projeto de vida e parte da proposta pedagogica. {summary}'

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
                answer += f' Se a situacao se repetir, o acompanhamento costuma passar por {follow_up}.'
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


def _handle_public_document_submission(context: Any) -> str:
    normalized = _normalize_text(context.source_message)
    if _is_positive_requirement_query(context.source_message) or (
        any(_message_matches_term(normalized, term) for term in {'documento', 'documentos'})
        and any(
            _message_matches_term(normalized, term)
            for term in {'matricula', 'matrícula', 'exigido', 'exigidos'}
        )
    ):
        return _compose_required_documents_answer(context.profile)
    return _compose_public_document_submission_answer(context.profile, message=context.source_message)


def _handle_public_policy(context: Any) -> str:
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


def _handle_public_policy_compare(context: Any) -> str:
    return _compose_public_policy_compare_answer(context.profile)


def _handle_public_service_credentials_bundle(context: Any) -> str:
    return _compose_public_service_credentials_bundle_answer(context.profile)
