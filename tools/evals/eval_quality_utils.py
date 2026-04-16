from __future__ import annotations

import difflib
import re
import unicodedata
from typing import Any

ERROR_WEIGHTS = {
    'request_failed': 60,
    'forbidden_entity_or_value': 45,
    'multi_intent_partial_collapse': 26,
    'partial_scope_loss': 22,
    'comparative_reasoning_mismatch': 22,
    'attendance_metric_misroute': 24,
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
    'weak_actionability': 10,
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
                    'expected_sections': [str(section) for section in (item.get('expected_sections') or []) if str(section).strip()],
                    'rubric_tags': [str(tag) for tag in (item.get('rubric_tags') or []) if str(tag).strip()],
                    'id': str(item.get('id') or ''),
                    'thread_id': str(item.get('thread_id') or ''),
                    'turn_index': int(item.get('turn_index') or 1),
                    'note': str(item.get('note') or ''),
                    'telegram_chat_id': item.get('telegram_chat_id'),
                    'user': item.get('user'),
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
                        'expected_sections': [str(section) for section in (turn.get('expected_sections') or []) if str(section).strip()],
                        'rubric_tags': [str(tag) for tag in (turn.get('rubric_tags') or []) if str(tag).strip()],
                        'id': str(turn.get('id') or entry.get('id') or f'{thread_id}_turn_{turn_index}'),
                        'thread_id': thread_id,
                        'turn_index': turn_index,
                        'note': str(turn.get('note') or ''),
                        'telegram_chat_id': turn.get('telegram_chat_id', entry.get('telegram_chat_id')),
                        'user': turn.get('user', entry.get('user')),
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
                'expected_sections': [str(section) for section in (entry.get('expected_sections') or []) if str(section).strip()],
                'rubric_tags': [str(tag) for tag in (entry.get('rubric_tags') or []) if str(tag).strip()],
                'id': str(entry.get('id') or ''),
                'thread_id': str(entry.get('thread_id') or ''),
                'turn_index': int(entry.get('turn_index') or 1),
                'note': str(entry.get('note') or ''),
                'telegram_chat_id': entry.get('telegram_chat_id'),
                'user': entry.get('user'),
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


_SEMANTIC_BUCKET_MARKERS: dict[str, tuple[str, ...]] = {
    'contacts': ('telefone', 'whatsapp', 'email', 'direcao', 'direção', 'secretaria', 'financeiro', 'contato', 'canal'),
    'pricing': ('mensalidade', 'matricula', 'matrícula', 'bolsa', 'desconto', 'valores', 'simulacao', 'simulação'),
    'timeline': ('calendario', 'calendário', 'aulas', 'reuniao', 'reunião', 'responsaveis', 'responsáveis', 'datas'),
    'portal_docs': ('portal', 'credenciais', 'login', 'senha', 'documentos', 'documentacao', 'documentação', 'secretaria'),
    'academic': ('nota', 'notas', 'media', 'média', 'avaliac', 'prova', 'frequencia', 'frequência', 'disciplina'),
    'finance': ('boleto', 'mensalidade', 'pagamento', 'financeiro', 'fatura', 'em aberto', 'vencimento'),
    'admin': ('cadastro', 'documentacao', 'documentação', 'pendencia', 'pendência', 'regularizar', 'bloqueio'),
    'restricted': ('interno', 'manual', 'playbook', 'protocolo interno', 'orientacao interna', 'orientação interna'),
    'public': ('publico', 'publica', 'material publico', 'base publica', 'documentos publicos', 'canais oficiais'),
}


def _semantic_buckets_for_text(value: str) -> set[str]:
    normalized = _normalize_match_text(value)
    buckets: set[str] = set()
    for bucket, markers in _SEMANTIC_BUCKET_MARKERS.items():
        if any(marker in normalized for marker in markers):
            buckets.add(bucket)
    return buckets


def _looks_like_multi_intent_partial_collapse(
    *,
    prompt: str,
    answer_text: str,
    expected_sections: list[str],
    rubric_tags: list[str],
    expected_keywords: list[str],
) -> bool:
    if expected_keywords and _contains_expected_keywords(answer_text, expected_keywords):
        return False
    requested = set(expected_sections) or _semantic_buckets_for_text(prompt)
    if 'multi_intent' in {tag.strip() for tag in rubric_tags}:
        requested = requested or {'contacts', 'pricing'}
    if len(requested) < 2:
        return False
    covered = _semantic_buckets_for_text(answer_text)
    overlap = requested & covered
    if not overlap:
        return True
    return len(overlap) < min(2, len(requested))


def _looks_like_partial_scope_loss(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    normalized_answer = _normalize_match_text(answer_text)
    scoped = any(marker in normalized_prompt for marker in ('isolar', 'isolando', 'somente', 'apenas', 'so a', 'só a'))
    named_student = next((name for name in ('ana oliveira', 'lucas oliveira', 'ana', 'lucas') if name in normalized_prompt), None)
    if not scoped or named_student is None:
        return False
    return named_student not in normalized_answer


def _looks_like_attendance_metric_misroute(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    normalized_answer = _normalize_match_text(answer_text)
    attendance_prompt = any(
        marker in normalized_prompt
        for marker in ('frequencia', 'frequência', 'faltas', 'falta', 'atrasos', 'presenca', 'presença')
    )
    if not attendance_prompt:
        return False
    attendance_answer = any(
        marker in normalized_answer
        for marker in ('frequencia', 'frequência', 'faltas', 'falta', 'atrasos', 'presenca', 'presença')
    )
    if attendance_answer:
        return False
    grade_answer = any(
        marker in normalized_answer
        for marker in ('nota', 'notas', 'media', 'média', 'boletim', 'aprovacao', 'aprovação', 'disciplina', 'academico', 'acadêmico')
    )
    return grade_answer


def _looks_like_comparative_reasoning_mismatch(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    if 'panorama academico' not in normalized_prompt or 'media minima' not in normalized_prompt:
        return False
    body_text = str(answer_text or '').split('[debug]', 1)[0]
    student_minima: dict[str, float] = {}
    for raw_line in body_text.splitlines():
        line = raw_line.strip()
        match = re.match(r'^-\s*([^:]+):\s*(.+)$', line)
        if not match:
            continue
        student_name = match.group(1).strip()
        values = [
            float(fragment.replace(',', '.'))
            for fragment in re.findall(r'(\d+[.,]\d+)', match.group(2))
        ]
        if values:
            student_minima[student_name] = min(values)
    if len(student_minima) < 2:
        return False
    lowest_student, lowest_value = min(
        student_minima.items(),
        key=lambda item: (item[1], _normalize_match_text(item[0])),
    )
    if lowest_value >= 7.0:
        return False
    lowered_body = body_text.casefold()
    if 'quem hoje' not in lowered_body:
        return False
    trailing = lowered_body.split('quem hoje', 1)[1]
    chosen_student = next(
        (
            student_name
            for student_name in student_minima
            if student_name.casefold() in trailing
        ),
        None,
    )
    if chosen_student is None:
        return False
    return _normalize_match_text(chosen_student) != _normalize_match_text(lowest_student)


def _looks_like_weak_actionability(prompt: str, answer_text: str) -> bool:
    normalized_prompt = _normalize_match_text(prompt)
    persona_framing_prefixes = (
        'como aluno autenticado',
        'como aluna autenticada',
        'como professor',
        'como professora',
        'como responsavel autenticado',
        'como responsável autenticado',
        'como guardian autenticado',
        'como estudante autenticado',
    )
    persona_framing = normalized_prompt.startswith(persona_framing_prefixes)
    has_actionability_anchor = any(
        marker in normalized_prompt
        for marker in ('na pratica', 'sequencia', 'sequência', 'proximo passo', 'próximo passo', 'o que fazer')
    ) or ('como' in normalized_prompt and not persona_framing)
    if not has_actionability_anchor:
        return False
    normalized_answer = _normalize_match_text(answer_text)
    if 'dividir o ano' in normalized_prompt and all(
        marker in normalized_answer for marker in ('admiss', 'rotina', 'fechamento')
    ):
        return False
    actionable_markers = (
        'primeiro',
        'depois',
        'canal',
        'setor',
        'protocolo',
        'secretaria',
        'portal',
        'passo',
        'encaminh',
    )
    return not any(marker in normalized_answer for marker in actionable_markers)


def _detect_error_types(
    *,
    answer_text: str,
    expected_keywords: list[str],
    forbidden_keywords: list[str],
    expected_sections: list[str] | None = None,
    rubric_tags: list[str] | None = None,
    prompt: str,
    previous_answer: str,
    status: int,
    turn_index: int,
    note: str,
) -> list[str]:
    expected_sections = list(expected_sections or [])
    rubric_tags = list(rubric_tags or [])
    if status != 200:
        return ['request_failed']
    normalized_answer = answer_text.casefold().strip()
    normalized_note = note.casefold().strip()
    errors: list[str] = []
    if expected_keywords and not _contains_expected_keywords(answer_text, expected_keywords):
        errors.append('missing_expected_keyword')
    if _contains_forbidden_keywords(answer_text, forbidden_keywords):
        errors.append('forbidden_entity_or_value')
    if _looks_like_multi_intent_partial_collapse(
        prompt=prompt,
        answer_text=answer_text,
        expected_sections=expected_sections,
        rubric_tags=rubric_tags,
        expected_keywords=expected_keywords,
    ):
        errors.append('multi_intent_partial_collapse')
    if _looks_like_partial_scope_loss(prompt, answer_text):
        errors.append('partial_scope_loss')
    if _looks_like_comparative_reasoning_mismatch(prompt, answer_text):
        errors.append('comparative_reasoning_mismatch')
    if _looks_like_attendance_metric_misroute(prompt, answer_text):
        errors.append('attendance_metric_misroute')
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
    if _looks_like_weak_actionability(prompt, answer_text):
        errors.append('weak_actionability')
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
