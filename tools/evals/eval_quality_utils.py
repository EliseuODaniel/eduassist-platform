from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Any

ERROR_WEIGHTS = {
    'request_failed': 60,
    'forbidden_entity_or_value': 45,
    'public_explanatory_misroute': 35,
    'generic_profile_leak': 28,
    'ungrounded_general_knowledge': 24,
    'empty_response': 30,
    'strict_safe_fallback_excess': 24,
    'pilot_unavailable_fallback': 18,
    'repair_miss': 18,
    'followup_context_drop': 25,
    'missing_expected_keyword': 20,
    'unnecessary_clarification': 12,
    'repetitive_reply': 10,
    'canned_tone': 8,
}

QUALITY_SIGNAL_NAMES = (
    'repair_ack',
    'followup_adaptation',
    'personalization',
)


def _infer_slice(prompt: str) -> str:
    lowered = prompt.lower()
    support_terms = (
        'atendente humano',
        'atendimento humano',
        'quero falar com um humano',
        'preciso falar com um humano',
        'como falo com um atendente',
        'quero falar com o setor',
        'suporte humano',
        'atendente',
        'humano',
        'ticket operacional',
        'atd-',
    )
    if any(term in lowered for term in support_terms):
        return 'support'
    workflow_terms = (
        'visita',
        'tour',
        'protocolar',
        'protocolo',
        'solicitacao',
        'solicitação',
        'remarcar',
        'reagendar',
        'cancelar a visita',
        'resume meu pedido',
        'status da visita',
        'status do protocolo',
    )
    if any(term in lowered for term in workflow_terms):
        return 'workflow'
    protected_terms = (
        'nota',
        'notas',
        'falta',
        'faltas',
        'frequencia',
        'prova',
        'provas',
        'avaliacao',
        'avaliacoes',
        'financeiro',
        'boleto',
        'pagamento',
        'mensalidade',
        'documentacao',
        'documentos',
        'meus filhos',
        'meu filho',
        'minha filha',
        'estou logado',
        'meu acesso',
        'lucas',
        'ana',
    )
    return 'protected' if any(term in lowered for term in protected_terms) else 'public'


def _normalize_prompt_entries(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise SystemExit('Prompt file must be a JSON list.')
    entries: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, str):
            entries.append({'prompt': item, 'slice': _infer_slice(item), 'category': 'uncategorized', 'expected_keywords': []})
            continue
        if isinstance(item, dict) and isinstance(item.get('turns'), list):
            entries.append(item)
            continue
        if isinstance(item, dict) and isinstance(item.get('prompt'), str):
            prompt = item['prompt']
            slice_name = str(item.get('slice') or _infer_slice(prompt))
            category = str(item.get('category') or 'uncategorized')
            expected_keywords = [str(keyword) for keyword in (item.get('expected_keywords') or []) if str(keyword).strip()]
            forbidden_keywords = [str(keyword) for keyword in (item.get('forbidden_keywords') or []) if str(keyword).strip()]
            entries.append(
                {
                    'prompt': prompt,
                    'slice': slice_name,
                    'category': category,
                    'expected_keywords': expected_keywords,
                    'forbidden_keywords': forbidden_keywords,
                    'thread_id': str(item.get('thread_id') or ''),
                    'turn_index': int(item.get('turn_index') or 1),
                    'note': str(item.get('note') or ''),
                    'telegram_chat_id': item.get('telegram_chat_id'),
                }
            )
            continue
        raise SystemExit('Each prompt entry must be a string or an object with a prompt field.')
    return entries


def _expand_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    expanded: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        if isinstance(entry.get('turns'), list):
            thread_id = str(entry.get('thread_id') or f'thread_{index}')
            default_slice = str(entry.get('slice') or 'public')
            default_category = str(entry.get('category') or 'threaded')
            for turn_index, turn in enumerate(entry['turns'], start=1):
                if not isinstance(turn, dict) or not isinstance(turn.get('prompt'), str):
                    raise SystemExit('Each threaded turn must be an object with a prompt field.')
                prompt = str(turn['prompt'])
                expanded.append(
                    {
                        'prompt': prompt,
                        'slice': str(turn.get('slice') or default_slice or _infer_slice(prompt)),
                        'category': str(turn.get('category') or default_category),
                        'expected_keywords': [str(keyword) for keyword in (turn.get('expected_keywords') or []) if str(keyword).strip()],
                        'forbidden_keywords': [str(keyword) for keyword in (turn.get('forbidden_keywords') or []) if str(keyword).strip()],
                        'thread_id': thread_id,
                        'turn_index': turn_index,
                        'note': str(turn.get('note') or ''),
                        'telegram_chat_id': turn.get('telegram_chat_id', entry.get('telegram_chat_id')),
                    }
                )
            continue
        expanded.append(
            {
                'prompt': str(entry['prompt']),
                'slice': str(entry.get('slice') or _infer_slice(str(entry['prompt']))),
                'category': str(entry.get('category') or 'uncategorized'),
                'expected_keywords': [str(keyword) for keyword in (entry.get('expected_keywords') or []) if str(keyword).strip()],
                'forbidden_keywords': [str(keyword) for keyword in (entry.get('forbidden_keywords') or []) if str(keyword).strip()],
                'thread_id': str(entry.get('thread_id') or ''),
                'turn_index': int(entry.get('turn_index') or 1),
                'note': str(entry.get('note') or ''),
                'telegram_chat_id': entry.get('telegram_chat_id'),
            }
        )
    return expanded


def _extract_answer_text(body: dict[str, Any] | str) -> str:
    if isinstance(body, str):
        return body
    if not isinstance(body, dict):
        return ''
    if isinstance(body.get('message_text'), str):
        return str(body['message_text'])
    metadata = body.get('metadata')
    if isinstance(metadata, dict):
        answer = metadata.get('answer')
        if isinstance(answer, dict) and isinstance(answer.get('answer_text'), str):
            return str(answer['answer_text'])
    return ''


def _normalize_match_text(value: str) -> str:
    text = unicodedata.normalize('NFKD', str(value or ''))
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    text = text.casefold()
    text = re.sub(r'[-_/]+', '', text)
    text = re.sub(r'[^0-9a-z]+', ' ', text)
    text = re.sub(r'(?<=\d)\s+(?=\d)', '', text)
    return ' '.join(text.split())


def _contains_expected_keywords(answer_text: str, expected_keywords: list[str]) -> bool:
    if not expected_keywords:
        return True
    normalized_answer = _normalize_match_text(answer_text)
    return all(_normalize_match_text(keyword) in normalized_answer for keyword in expected_keywords)


def _contains_forbidden_keywords(answer_text: str, forbidden_keywords: list[str]) -> bool:
    if not forbidden_keywords:
        return False
    normalized_answer = _normalize_match_text(answer_text)
    raw_answer = str(answer_text or '').casefold()
    for keyword in forbidden_keywords:
        raw_keyword = str(keyword or '')
        if not raw_keyword.strip():
            continue
        normalized_keyword = _normalize_match_text(raw_keyword)
        if normalized_keyword:
            if normalized_keyword in normalized_answer:
                return True
            continue
        if raw_keyword.casefold() in raw_answer:
            return True
    return False


def _looks_like_public_explanatory_prompt(prompt: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    explanatory_markers = (
        'quais evidencias',
        'material publico',
        'base publica',
        'sem entrar em dados privados',
        'quero entender',
        'quero uma leitura ampla',
        'como a escola',
        'como o material publico',
        'como frequencia',
        'como pontualidade',
    )
    return any(marker in normalized_prompt for marker in explanatory_markers)


def _looks_like_public_bundle_prompt(prompt: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    topic_terms = (
        'inclus',
        'acess',
        'integral',
        'estudo orientado',
        'medic',
        'emerg',
        'saida',
        'autoriz',
        'transporte',
        'uniforme',
        'aliment',
        'direcao',
        'protocolo',
        'frequencia',
        'pontualidade',
        'convivencia',
    )
    return sum(1 for term in topic_terms if term in normalized_prompt) >= 2


def _looks_like_public_explanatory_misroute(prompt: str, answer_text: str) -> bool:
    if not _looks_like_public_explanatory_prompt(prompt):
        return False
    normalized_answer = _normalize_match_text(answer_text)
    request_markers = (
        'abrir um protocolo',
        'abrir protocolo',
        'abrir um pedido',
        'abrir uma solicitacao',
        'abrir uma solicitacao',
        'registrar um protocolo',
        'registrar um pedido',
        'registrar uma solicitacao',
        'encaminhar para direcao',
        'encaminhar para a direcao',
        'posso abrir',
        'posso registrar',
        'posso encaminhar',
        'posso acionar',
    )
    return any(marker in normalized_answer for marker in request_markers)


def _looks_like_generic_profile_leak(prompt: str, answer_text: str) -> bool:
    if not _looks_like_public_bundle_prompt(prompt):
        return False
    normalized_answer = _normalize_match_text(answer_text)
    profile_markers = (
        'instituicao laica',
        'proposta pedagogica',
        'ensino fundamental ii',
        'ensino medio',
        'tecnologia',
        'diferenciais',
        'projeto de vida',
        'colegio horizonte e uma escola',
    )
    marker_count = sum(1 for marker in profile_markers if marker in normalized_answer)
    bundle_markers = (
        'acessib',
        'integral',
        'estudo orientado',
        'medic',
        'emerg',
        'autoriz',
        'saida',
        'transporte',
        'uniforme',
        'direcao',
        'protocolo',
        'pontualidade',
        'frequencia',
        'convivencia',
    )
    bundle_count = sum(1 for marker in bundle_markers if marker in normalized_answer)
    return marker_count >= 2 and bundle_count <= 1


def _looks_like_ungrounded_general_knowledge(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    normalized_answer = _normalize_match_text(answer_text)
    if (
        'escola' not in normalized_prompt
        and 'material publico' not in normalized_prompt
        and 'base publica' not in normalized_prompt
        and 'orientacoes publicas' not in normalized_prompt
    ):
        return False
    general_markers = (
        'em geral',
        'normalmente',
        'de modo geral',
        'via de regra',
        'costuma',
        'em muitas escolas',
        'geralmente',
    )
    if not any(marker in normalized_answer for marker in general_markers):
        return False
    grounding_markers = (
        'colegio horizonte',
        'na escola',
        'material publico',
        'base publica',
        'documentos publicos',
        'calendario publico',
        'canais oficiais',
        'portal institucional',
        'conta vinculada',
        'login',
    )
    return not any(marker in normalized_answer for marker in grounding_markers)


def _looks_like_empty_response(answer_text: str) -> bool:
    normalized_answer = _normalize_match_text(answer_text)
    return normalized_answer in {'', 'empty response'}


def _looks_like_strict_safe_fallback_excess(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    normalized_answer = _normalize_match_text(answer_text)
    fallback_markers = (
        'nao consegui concluir essa resposta premium agora',
        'nao consegui consolidar essa resposta premium com seguranca agora',
        'reformule em uma frase mais direta',
    )
    return _looks_like_public_explanatory_prompt(normalized_prompt) and any(
        marker in normalized_answer for marker in fallback_markers
    )


def _looks_like_pilot_unavailable_fallback(answer_text: str) -> bool:
    normalized_answer = _normalize_match_text(answer_text)
    return 'dependencia indisponivel' in normalized_answer or 'dependency unavailable' in normalized_answer


def _detect_error_types(
    *,
    answer_text: str,
    expected_keywords: list[str],
    forbidden_keywords: list[str],
    prompt: str,
    previous_answer: str,
    status: int,
    turn_index: int,
    note: str,
) -> list[str]:
    if status != 200:
        return ['request_failed']
    normalized_answer = answer_text.casefold().strip()
    normalized_note = note.casefold().strip()
    errors: list[str] = []
    if expected_keywords and not _contains_expected_keywords(answer_text, expected_keywords):
        errors.append('missing_expected_keyword')
    if _contains_forbidden_keywords(answer_text, forbidden_keywords):
        errors.append('forbidden_entity_or_value')
    if _looks_like_public_explanatory_misroute(prompt, answer_text):
        errors.append('public_explanatory_misroute')
    if _looks_like_generic_profile_leak(prompt, answer_text):
        errors.append('generic_profile_leak')
    if _looks_like_ungrounded_general_knowledge(prompt, answer_text):
        errors.append('ungrounded_general_knowledge')
    if _looks_like_empty_response(answer_text):
        errors.append('empty_response')
    if _looks_like_strict_safe_fallback_excess(prompt, answer_text):
        errors.append('strict_safe_fallback_excess')
    if _looks_like_pilot_unavailable_fallback(answer_text):
        errors.append('pilot_unavailable_fallback')
    if expected_keywords and '?' in answer_text:
        errors.append('unnecessary_clarification')
    if turn_index > 1 and previous_answer:
        similarity = difflib.SequenceMatcher(a=previous_answer.casefold().strip(), b=normalized_answer).ratio()
        repeated_auth_guidance = (
            'essa consulta depende de autenticacao e vinculo da sua conta no telegram' in normalized_answer
            and 'current state drift' in normalized_note
        )
        if similarity >= 0.92 and not repeated_auth_guidance:
            errors.append('repetitive_reply')
        if prompt.casefold().strip().startswith('e ') and expected_keywords and not _contains_expected_keywords(answer_text, expected_keywords):
            errors.append('followup_context_drop')
    if 'repair' in normalized_note:
        repair_markers = (
            'desculp',
            'corrig',
            'voce esta certo',
            'você está certo',
            'houve um erro',
            'confus',
            'sem problema',
            'comecar do zero',
            'começar do zero',
        )
        if not any(marker in normalized_answer for marker in repair_markers):
            errors.append('repair_miss')
    canned_markers = (
        'por aqui eu consigo te ajudar',
        'se quiser, pode me dizer direto',
        'se precisar de mais alguma informacao',
        'e so me avisar',
    )
    if any(marker in normalized_answer for marker in canned_markers) and expected_keywords:
        errors.append('canned_tone')
    return sorted(set(errors))


def _needs_personalization(prompt: str, expected_keywords: list[str]) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    if any(term in normalized_prompt.split() for term in ('meu', 'minha', 'meus', 'minhas', 'dele', 'dela')):
        return True
    if any(term in normalized_prompt for term in ('lucas', 'ana', 'joao', 'joão', 'maria', 'sofia')):
        return True
    return any(' ' in str(keyword).strip() for keyword in expected_keywords)


def _detect_quality_signals(
    *,
    answer_text: str,
    expected_keywords: list[str],
    prompt: str,
    previous_answer: str,
    turn_index: int,
    note: str,
) -> dict[str, bool | None]:
    normalized_answer = answer_text.casefold().strip()
    normalized_note = note.casefold().strip()
    followup_prompt = prompt.casefold().strip().startswith(('e ', 'mas '))
    repair_eligible = 'repair' in normalized_note
    personalization_eligible = _needs_personalization(prompt, expected_keywords)
    repair_markers = (
        'desculp',
        'corrig',
        'voce esta certo',
        'você está certo',
        'houve um erro',
        'confus',
        'sem problema',
        'comecar do zero',
        'começar do zero',
    )
    return {
        'repair_ack': (any(marker in normalized_answer for marker in repair_markers) if repair_eligible else None),
        'followup_adaptation': (
            (not previous_answer or difflib.SequenceMatcher(a=previous_answer.casefold().strip(), b=normalized_answer).ratio() < 0.92)
            if turn_index > 1 and followup_prompt
            else None
        ),
        'personalization': (
            (not expected_keywords or _contains_expected_keywords(answer_text, expected_keywords))
            if personalization_eligible
            else None
        ),
    }


def _quality_score(*, status: int, error_types: list[str]) -> int:
    if status != 200:
        return 0
    penalty = sum(ERROR_WEIGHTS.get(error_type, 5) for error_type in error_types)
    return max(0, 100 - penalty)
