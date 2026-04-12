from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Suggested replies, visuals, and actor-scope interaction helpers extracted from runtime_core.py."""

from . import runtime_core as _runtime_core


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _workflow_contextual_suggested_replies(
    *,
    preview: Any,
    conversation_context: dict[str, Any] | None,
) -> list[str] | None:
    recent_focus = _recent_conversation_focus(conversation_context)
    if not recent_focus:
        return None
    kind = recent_focus.get('kind')
    if 'get_workflow_status' in preview.selected_tools:
        if kind == 'visit':
            return [
                'Tem alguma atualizacao da visita?',
                'Qual o proximo passo da visita?',
                'Quero remarcar a visita',
                'Quero cancelar a visita',
            ]
        if kind == 'request':
            return [
                'Tem alguma atualizacao?',
                'Qual o proximo passo?',
                'Complementar meu pedido',
                'Resume meu pedido',
            ]
    if 'update_visit_booking' in preview.selected_tools or kind == 'visit':
        return [
            'Tem alguma atualizacao da visita?',
            'Qual o proximo passo da visita?',
            'Quero cancelar a visita',
            'Quero remarcar a visita',
        ]
    if 'update_institutional_request' in preview.selected_tools or kind == 'request':
        return [
            'Tem alguma atualizacao?',
            'Qual o proximo passo?',
            'Complementar meu pedido',
            'Resume meu pedido',
        ]
    return None


def _recent_protected_student_name(
    actor: dict[str, Any] | None,
    *,
    capability: str,
    message: str | None = None,
    conversation_context: dict[str, Any] | None,
) -> str | None:
    student: dict[str, Any] | None = None
    if message:
        student, _clarification = _select_linked_student(
            actor,
            message,
            capability=capability,
            conversation_context=conversation_context,
        )
    if student is None:
        student = _recent_student_from_context(
            actor,
            capability=capability,
            conversation_context=conversation_context,
        )
    if student is None:
        return None
    full_name = str(student.get('full_name', '')).strip()
    if not full_name:
        return None
    return full_name.split()[0]


def _protected_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[str]:
    role_code = str((actor or {}).get('role_code', 'anonymous'))
    if preview.classification.domain is QueryDomain.finance:
        student_name = _recent_protected_student_name(
            actor,
            capability='finance',
            message=request.message,
            conversation_context=conversation_context,
        )
        if student_name:
            return [
                f'Quais boletos do {student_name} estao em aberto?',
                f'Tem alguma fatura vencida do {student_name}?',
                f'Preciso da segunda via do {student_name}',
                f'E as notas do {student_name}?',
            ]
        return [
            'Quais boletos estao em aberto?',
            'Tem alguma fatura vencida?',
            'Preciso da segunda via',
            'Qual a mensalidade?',
        ]
    if role_code == 'teacher':
        return [
            'Quais turmas eu tenho?',
            'Mostre minha agenda',
            'Qual o horario de hoje?',
            'Tem aula substituta?',
        ]
    student_name = _recent_protected_student_name(
        actor,
        capability='academic',
        message=request.message,
        conversation_context=conversation_context,
    )
    if student_name:
        return [
            f'E a frequencia do {student_name}?',
            f'E o financeiro do {student_name}?',
            f'Mostre um grafico das notas do {student_name}',
            f'Qual o calendario da turma do {student_name}?',
        ]
    return [
        'Mostre as notas',
        'Quais sao as faltas?',
        'Tem prova marcada?',
        'Qual o calendario da turma?',
    ]


def _support_suggested_replies(
    *, preview: Any, conversation_context: dict[str, Any] | None
) -> list[str]:
    contextual = _workflow_contextual_suggested_replies(
        preview=preview,
        conversation_context=conversation_context,
    )
    if contextual:
        return contextual
    if 'get_workflow_status' in preview.selected_tools:
        return [
            'Qual o prazo?',
            'Quem vai me responder?',
            'Qual o protocolo?',
            'Complementar meu pedido',
        ]
    if 'update_visit_booking' in preview.selected_tools:
        return [
            'Qual o status da visita?',
            'Qual o protocolo da visita?',
            'Quero cancelar a visita',
            'Quero remarcar a visita',
        ]
    if 'update_institutional_request' in preview.selected_tools:
        return [
            'Qual o status do meu protocolo?',
            'Qual o prazo?',
            'Quem vai me responder?',
            'Resume meu pedido',
        ]
    if 'schedule_school_visit' in preview.selected_tools:
        return [
            'Qual o status da visita?',
            'Qual o prazo?',
            'Quem vai me responder?',
            'Mudar horario da visita',
        ]
    return [
        'Qual o status do meu protocolo?',
        'Qual o prazo?',
        'Quem vai me responder?',
        'E agora?',
    ]


def _deny_suggested_replies() -> list[str]:
    return [
        'Como vinculo minha conta?',
        'Mensalidade do ensino medio',
        'Agendar visita',
        'Quais opcoes de assuntos eu tenho aqui?',
    ]


def _build_suggested_replies(
    *,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None,
) -> list[MessageResponseSuggestedReply]:
    # This module is imported while runtime_core is still wiring extracted namespaces.
    # Refresh lazily at call time so helpers moved to sibling extracted modules remain available.
    _export_runtime_core_namespace()
    from .workflow_runtime import (
        _dedupe_suggested_replies as workflow_dedupe_suggested_replies,
    )
    from .workflow_runtime import (
        _default_public_suggested_replies as workflow_default_public_suggested_replies,
    )
    from .workflow_runtime import (
        _institution_suggested_replies as workflow_institution_suggested_replies,
    )
    candidate_texts: list[str]
    if preview.mode is OrchestrationMode.deny:
        candidate_texts = _deny_suggested_replies()
    elif (
        preview.classification.domain is QueryDomain.support
        and preview.mode is OrchestrationMode.structured_tool
    ):
        candidate_texts = _support_suggested_replies(
            preview=preview, conversation_context=conversation_context
        )
    elif (
        preview.classification.domain in {QueryDomain.academic, QueryDomain.finance}
        and preview.mode is OrchestrationMode.structured_tool
    ):
        candidate_texts = _protected_suggested_replies(
            request=request,
            preview=preview,
            actor=actor,
            conversation_context=conversation_context,
        )
    elif preview.classification.domain is QueryDomain.institution:
        candidate_texts = workflow_institution_suggested_replies(
            request=request,
            preview=preview,
            school_profile=school_profile,
            conversation_context=conversation_context,
        )
    elif preview.classification.domain is QueryDomain.calendar:
        candidate_texts = [
            'Quando e a proxima reuniao de pais?',
            'Quando comecam as aulas?',
            'Qual o horario do 9o ano?',
            'Agendar visita',
        ]
    else:
        candidate_texts = workflow_default_public_suggested_replies()
    return workflow_dedupe_suggested_replies(candidate_texts)


def _wants_visual_response(message: str) -> bool:
    from .public_act_rules_runtime import _contains_any as public_contains_any

    return public_contains_any(message, VISUAL_TERMS)


def _load_font(size: int):
    try:
        return ImageFont.truetype('DejaVuSans.ttf', size=size)
    except Exception:  # pragma: no cover - font availability depends on runtime image
        return ImageFont.load_default()


def _build_visual_asset(
    *, title: str, subtitle: str, labels: list[str], values: list[float], unit: str
) -> MessageResponseVisualAsset | None:
    if not labels or not values or len(labels) != len(values):
        return None

    width, height = 1280, 820
    padding_left, padding_right = 110, 80
    padding_top, padding_bottom = 110, 120
    plot_width = width - padding_left - padding_right
    plot_height = height - padding_top - padding_bottom
    bar_gap = 28
    bar_width = max(48, int((plot_width - bar_gap * (len(values) - 1)) / max(len(values), 1)))
    max_value = max(max(values), 1.0)

    image = Image.new('RGB', (width, height), '#f6f3ee')
    draw = ImageDraw.Draw(image)
    title_font = _load_font(38)
    subtitle_font = _load_font(22)
    axis_font = _load_font(20)
    label_font = _load_font(18)

    draw.text((padding_left, 28), title, font=title_font, fill='#16213a')
    if subtitle:
        draw.text((padding_left, 72), subtitle, font=subtitle_font, fill='#556070')

    axis_x0 = padding_left
    axis_y0 = padding_top
    axis_x1 = padding_left
    axis_y1 = padding_top + plot_height
    axis_x2 = padding_left + plot_width
    axis_y2 = axis_y1
    draw.line((axis_x0, axis_y0, axis_x1, axis_y1), fill='#5c6470', width=3)
    draw.line((axis_x1, axis_y1, axis_x2, axis_y2), fill='#5c6470', width=3)

    palette = ['#0f766e', '#1d4ed8', '#c2410c', '#7c3aed', '#b45309', '#0f172a']
    for index, value in enumerate(values):
        x0 = padding_left + index * (bar_width + bar_gap)
        x1 = x0 + bar_width
        ratio = value / max_value if max_value else 0
        bar_height = int(ratio * (plot_height - 30))
        y0 = padding_top + plot_height - bar_height
        y1 = padding_top + plot_height
        color = palette[index % len(palette)]
        draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=color)
        value_label = (
            f'{value:.1f}{unit}'.rstrip('0').rstrip('.') if unit != '%' else f'{value:.1f}%'
        )
        draw.text((x0, y0 - 28), value_label, font=axis_font, fill='#16213a')
        draw.text((x0, y1 + 16), labels[index], font=label_font, fill='#16213a')

    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    encoded = base64.b64encode(buffer.getvalue()).decode('ascii')
    return MessageResponseVisualAsset(
        title=title,
        mime_type='image/png',
        base64_data=encoded,
        caption=subtitle or title,
    )


def _build_public_kpi_visual(
    profile: dict[str, Any], message: str
) -> list[MessageResponseVisualAsset]:
    entries = _select_public_kpis(profile, message)
    if not entries:
        return []
    labels = [str(item.get('label', 'Indicador'))[:18] for item in entries]
    values = [float(item.get('value', 0.0) or 0.0) for item in entries]
    asset = _build_visual_asset(
        title='Indicadores institucionais',
        subtitle='Painel publico mais recente',
        labels=labels,
        values=values,
        unit='%',
    )
    return [asset] if asset is not None else []


def _normalize_response_wording(message_text: str) -> str:
    normalized = str(message_text or '')
    replacements = {
        'enviar por e-mail para a secretaria': 'usar o email da secretaria',
        'o e-mail da secretaria': 'o email da secretaria',
        'E-mail da secretaria': 'Email da secretaria',
    }
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    return normalized


def _build_academic_visual(
    summary: dict[str, Any], message: str, student_name: str
) -> list[MessageResponseVisualAsset]:
    normalized = _normalize_text(message)
    if _contains_any(normalized, ATTENDANCE_TERMS) and not _contains_any(normalized, GRADE_TERMS):
        attendance_rows = summary.get('attendance')
        if not isinstance(attendance_rows, list) or not attendance_rows:
            return []
        labels = [
            str(item.get('subject_name', 'Disciplina'))[:18]
            for item in attendance_rows[:6]
            if isinstance(item, dict)
        ]
        values = []
        for item in attendance_rows[:6]:
            if not isinstance(item, dict):
                continue
            present = float(item.get('present_count', 0) or 0)
            late = float(item.get('late_count', 0) or 0)
            absent = float(item.get('absent_count', 0) or 0)
            total = present + late + absent
            values.append(round(((present + late) / total) * 100, 1) if total else 0.0)
        asset = _build_visual_asset(
            title=f'Frequencia de {student_name}',
            subtitle='Percentual de presenca por disciplina',
            labels=labels,
            values=values,
            unit='%',
        )
        return [asset] if asset is not None else []

    grades = summary.get('grades')
    if not isinstance(grades, list) or not grades:
        return []
    per_subject: dict[str, list[float]] = {}
    for item in grades:
        if not isinstance(item, dict):
            continue
        subject_name = str(item.get('subject_name', 'Disciplina'))
        score = float(item.get('score', 0) or 0)
        max_score = float(item.get('max_score', 0) or 0)
        if max_score <= 0:
            continue
        per_subject.setdefault(subject_name, []).append(round((score / max_score) * 100, 1))
    labels = list(per_subject.keys())[:6]
    values = [round(sum(per_subject[label]) / len(per_subject[label]), 1) for label in labels]
    asset = _build_visual_asset(
        title=f'Notas de {student_name}',
        subtitle='Media percentual por disciplina',
        labels=[label[:18] for label in labels],
        values=values,
        unit='%',
    )
    return [asset] if asset is not None else []


def _build_finance_visual(
    summary: dict[str, Any], student_name: str
) -> list[MessageResponseVisualAsset]:
    open_count = float(summary.get('open_invoice_count', 0) or 0)
    overdue_count = float(summary.get('overdue_invoice_count', 0) or 0)
    invoices = summary.get('invoices')
    paid_count = 0.0
    if isinstance(invoices, list):
        paid_count = float(
            sum(1 for item in invoices if isinstance(item, dict) and item.get('status') == 'paid')
        )
    asset = _build_visual_asset(
        title=f'Panorama financeiro de {student_name}',
        subtitle='Distribuicao de faturas na base atual',
        labels=['Em aberto', 'Vencidas', 'Pagas'],
        values=[open_count, overdue_count, paid_count],
        unit='',
    )
    return [asset] if asset is not None else []


async def _maybe_build_visual_assets(
    *,
    settings: Any,
    request: MessageResponseRequest,
    preview: Any,
    actor: dict[str, Any] | None,
    school_profile: dict[str, Any] | None,
    conversation_context: dict[str, Any] | None = None,
) -> list[MessageResponseVisualAsset]:
    from .protected_domain_runtime import _build_visual_specialists as protected_build_visual_specialists

    specialists = protected_build_visual_specialists(preview=preview, message=request.message)
    if not specialists:
        return []

    set_span_attributes(
        **{
            'eduassist.visual_manager.executed_specialists': ','.join(
                specialist.name for specialist in specialists
            ),
            'eduassist.visual_manager.executed_tools': ','.join(
                tool_name for specialist in specialists for tool_name in specialist.tool_names
            ),
        }
    )

    if preview.classification.domain is QueryDomain.institution:
        profile = school_profile or await _fetch_public_school_profile(settings=settings)
        if profile is None:
            return []
        return _build_public_kpi_visual(profile, request.message)

    if request.telegram_chat_id is None:
        return []

    actor = actor or await _fetch_actor_context(
        settings=settings, telegram_chat_id=request.telegram_chat_id
    )
    if actor is None:
        return []

    student, clarification = _select_linked_student(
        actor,
        request.message,
        capability='finance'
        if preview.classification.domain is QueryDomain.finance
        else 'academic',
        conversation_context=conversation_context,
    )
    if clarification is not None or student is None:
        return []
    student_id = student.get('student_id')
    student_name = str(student.get('full_name', 'Aluno'))
    if not isinstance(student_id, str):
        return []

    if preview.classification.domain is QueryDomain.academic:
        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/academic-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or not isinstance(payload, dict):
            return []
        summary = payload.get('summary')
        if not isinstance(summary, dict):
            return []
        return _build_academic_visual(summary, request.message, student_name)

    if preview.classification.domain is QueryDomain.finance:
        payload, status_code = await _api_core_get(
            settings=settings,
            path=f'/v1/students/{student_id}/financial-summary',
            params={'telegram_chat_id': request.telegram_chat_id},
        )
        if status_code != 200 or not isinstance(payload, dict):
            return []
        summary = payload.get('summary')
        if not isinstance(summary, dict):
            return []
        return _build_finance_visual(summary, student_name)

    return []


def _compose_handoff_answer(handoff_payload: dict[str, Any] | None) -> str:
    if not handoff_payload:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Posso seguir com orientacoes publicas por aqui, mas nao consegui registrar o encaminhamento humano agora',
                offer='Tente novamente em instantes ou use a secretaria',
            )
        )

    item = handoff_payload.get('item')
    if not isinstance(item, dict):
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead='Registrei a necessidade de atendimento humano, mas nao consegui recuperar o protocolo',
                offer='Use a secretaria para confirmar a fila',
            )
        )

    queue_name = str(item.get('queue_name', 'atendimento'))
    ticket_code = str(item.get('ticket_code', 'protocolo indisponivel'))
    status = str(item.get('status', 'queued'))
    created = bool(handoff_payload.get('created', False))

    if created:
        return _render_structured_answer_frame(
            StructuredAnswerFrame(
                lead=f'Encaminhei sua solicitacao para a fila de {queue_name}',
                facts=(
                    f'Protocolo: {ticket_code}',
                    f'Status atual: {status}',
                ),
                next_step='A equipe humana pode continuar esse atendimento no portal operacional',
            )
        )

    return _render_structured_answer_frame(
        StructuredAnswerFrame(
            lead=f'Sua solicitacao ja estava registrada na fila de {queue_name}',
            facts=(
                f'Protocolo: {ticket_code}',
                f'Status atual: {status}',
            ),
        )
    )
