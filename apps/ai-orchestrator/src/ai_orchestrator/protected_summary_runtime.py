from __future__ import annotations

# ruff: noqa: F401,F403,F405
"""Protected academic and finance summary helpers extracted from protected_domain_runtime.py."""

from . import runtime_core as _runtime_core
from .intent_analysis_runtime import _contains_any, _message_matches_term, _normalize_text


def _format_administrative_status(*args, **kwargs):
    from .protected_domain_runtime import _format_administrative_status as _impl

    return _impl(*args, **kwargs)


def _select_next_due_invoice(*args, **kwargs):
    from .protected_domain_runtime import _select_next_due_invoice as _impl

    return _impl(*args, **kwargs)


def _format_public_date_text(*args, **kwargs):
    from .public_profile_runtime import _format_public_date_text as _impl

    return _impl(*args, **kwargs)


def _export_runtime_core_namespace() -> None:
    for name, value in vars(_runtime_core).items():
        if name.startswith('__'):
            continue
        globals()[name] = value


_export_runtime_core_namespace()


def _format_grades(summary: dict[str, Any]) -> list[str]:
    grades = summary.get('grades')
    if not isinstance(grades, list) or not grades:
        return ['- Ainda nao ha lancamentos de notas no periodo consultado.']
    subject_rows: dict[str, dict[str, Any]] = {}
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = str(grade.get('subject_name', '') or '').strip()
        if not subject_name:
            continue
        subject_key = _normalize_text(subject_name)
        current = subject_rows.get(subject_key)
        if current is None:
            subject_rows[subject_key] = grade
            continue
        current_due = str(current.get('due_date', '') or '')
        candidate_due = str(grade.get('due_date', '') or '')
        if candidate_due and candidate_due > current_due:
            subject_rows[subject_key] = grade

    chosen = sorted(
        subject_rows.values(),
        key=lambda item: _normalize_text(str(item.get('subject_name', ''))),
    )[:8]
    if not chosen:
        chosen = [grade for grade in grades[:8] if isinstance(grade, dict)]

    lines = []
    for grade in chosen:
        lines.append(
            '- {subject_name} - {item_title}: {score}/{max_score}'.format(
                subject_name=grade.get('subject_name', 'Disciplina'),
                item_title=grade.get('item_title', 'Atividade'),
                score=grade.get('score', '?'),
                max_score=grade.get('max_score', '?'),
            )
        )
    return lines or ['- Ainda nao ha lancamentos de notas no periodo consultado.']


def _format_attendance(summary: dict[str, Any]) -> list[str]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list) or not attendance:
        return ['- Ainda nao ha registros consolidados de frequencia.']
    lines = []
    for row in attendance[:4]:
        if not isinstance(row, dict):
            continue
        lines.append(
            '- {subject_name}: {present} presencas, {late} atrasos, {absent} faltas ({minutes} min)'.format(
                subject_name=row.get('subject_name', 'Disciplina'),
                present=row.get('present_count', 0),
                late=row.get('late_count', 0),
                absent=row.get('absent_count', 0),
                minutes=row.get('absent_minutes', 0),
            )
        )
    return lines or ['- Ainda nao ha registros consolidados de frequencia.']


def _format_attendance_overview(summary: dict[str, Any]) -> list[str]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list) or not attendance:
        return ['- Ainda nao ha registros consolidados de frequencia neste recorte.']
    present = 0
    late = 0
    absent = 0
    minutes = 0
    for row in attendance:
        if not isinstance(row, dict):
            continue
        present += int(row.get('present_count', 0) or 0)
        late += int(row.get('late_count', 0) or 0)
        absent += int(row.get('absent_count', 0) or 0)
        minutes += int(row.get('absent_minutes', 0) or 0)
    return [
        f'- Presencas registradas: {present}',
        f'- Faltas registradas: {absent}',
        f'- Atrasos registrados: {late}',
        f'- Minutos somados de ausencia: {minutes}',
    ]


def _attendance_totals(summary: dict[str, Any]) -> tuple[int, int, int, int]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return 0, 0, 0, 0
    present = 0
    late = 0
    absent = 0
    minutes = 0
    for row in attendance:
        if not isinstance(row, dict):
            continue
        present += int(row.get('present_count', 0) or 0)
        late += int(row.get('late_count', 0) or 0)
        absent += int(row.get('absent_count', 0) or 0)
        minutes += int(row.get('absent_minutes', 0) or 0)
    return present, late, absent, minutes


def _attendance_priority_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    attendance = summary.get('attendance')
    if not isinstance(attendance, list):
        return []
    rows = [row for row in attendance if isinstance(row, dict)]
    rows.sort(
        key=lambda row: (
            -(int(row.get('absent_count', 0) or 0)),
            -(int(row.get('late_count', 0) or 0)),
            -(int(row.get('present_count', 0) or 0)),
            _normalize_text(str(row.get('subject_name', ''))),
        )
    )
    return rows


def _compose_family_attendance_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    if not summaries:
        return (
            'Nao encontrei panorama consolidado de frequencia das contas vinculadas neste recorte.'
        )

    lines = ['Panorama de frequencia das contas vinculadas:']
    strongest_name: str | None = None
    strongest_focus: str | None = None
    strongest_signature: tuple[int, int, int, int] | None = None

    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        present, late, absent, minutes = _attendance_totals(summary)
        top_row = next(iter(_attendance_priority_rows(summary)), None)
        line = (
            f'- {student_name}: {absent} falta(s), {late} atraso(s), '
            f'{present} presenca(s), {minutes} minuto(s) de ausencia.'
        )
        subject_name = None
        if isinstance(top_row, dict):
            subject_name = str(top_row.get('subject_name') or 'disciplina').strip() or 'disciplina'
            subject_absent = int(top_row.get('absent_count', 0) or 0)
            subject_late = int(top_row.get('late_count', 0) or 0)
            line += (
                f' Ponto mais sensivel: {subject_name} '
                f'({subject_absent} falta(s), {subject_late} atraso(s)).'
            )
        lines.append(line)
        signature = (absent, late, minutes, -present)
        if strongest_signature is None or signature > strongest_signature:
            strongest_signature = signature
            strongest_name = student_name
            strongest_focus = subject_name

    if strongest_name:
        closing = f'Quem exige maior atencao agora: {strongest_name}.'
        if strongest_focus:
            closing += f' O ponto mais sensivel aparece em {strongest_focus}.'
        lines.append(closing)
    return '\n'.join(lines)


def _academic_subject_averages(summary: dict[str, Any]) -> list[tuple[str, float]]:
    grades = summary.get('grades')
    if not isinstance(grades, list):
        return []
    grouped: dict[str, list[float]] = {}
    display_names: dict[str, str] = {}
    for grade in grades:
        if not isinstance(grade, dict):
            continue
        subject_name = str(grade.get('subject_name', '') or '').strip()
        if not subject_name:
            continue
        try:
            score = float(grade.get('score', 0) or 0)
            max_score = float(grade.get('max_score', 0) or 0)
        except (TypeError, ValueError):
            continue
        normalized_score = score if max_score <= 0 else (score / max_score) * 10.0
        subject_key = _normalize_text(subject_name)
        grouped.setdefault(subject_key, []).append(normalized_score)
        display_names[subject_key] = subject_name
    averages: list[tuple[str, float]] = []
    for subject_key, scores in grouped.items():
        if not scores:
            continue
        averages.append((display_names[subject_key], sum(scores) / len(scores)))
    averages.sort(key=lambda item: item[0])
    return averages


def _compose_academic_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    if not summaries:
        return 'Nao encontrei resumo academico consolidado das contas vinculadas neste recorte.'

    lines = ['Panorama academico das contas vinculadas:']
    highest_risk_student_name: str | None = None
    highest_risk_subject_name: str | None = None
    highest_risk_signature: tuple[int, float, str] | None = None

    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        averages = _academic_subject_averages(summary)
        if not averages:
            lines.append(f'- {student_name}: sem notas consolidadas neste recorte.')
            continue
        prioritized = [
            item
            for item in averages
            if _normalize_text(item[0])
            in {
                'historia',
                'história',
                'fisica',
                'física',
                'matematica',
                'matemática',
                'portugues',
                'português',
            }
        ]
        preview_items = prioritized[:4] or averages[:4]
        preview = '; '.join(
            f'{name} {value:.1f}'.replace('.', ',') for name, value in preview_items
        )
        lines.append(f'- {student_name}: {preview}')
        below_target = [(name, value) for name, value in averages if value < PASSING_GRADE_TARGET]
        if below_target:
            subject_name, value = min(
                below_target,
                key=lambda item: (item[1], _normalize_text(item[0])),
            )
            signature = (1, PASSING_GRADE_TARGET - value, student_name)
        else:
            subject_name, value = min(
                averages,
                key=lambda item: (abs(item[1] - PASSING_GRADE_TARGET), _normalize_text(item[0])),
            )
            signature = (0, PASSING_GRADE_TARGET - value, student_name)
        if highest_risk_signature is None or signature > highest_risk_signature:
            highest_risk_signature = signature
            highest_risk_student_name = student_name
            highest_risk_subject_name = subject_name

    if (
        highest_risk_student_name
        and highest_risk_subject_name
        and highest_risk_signature is not None
    ):
        lines.append(
            'Quem hoje exige maior atencao academica e '
            f'{highest_risk_student_name}, principalmente em {highest_risk_subject_name}.'
        )
    return '\n'.join(lines)


def _compose_academic_risk_answer(summary: dict[str, Any], *, student_name: str) -> str:
    averages = _academic_subject_averages(summary)
    if not averages:
        return (
            f'{student_name} e o foco desta consulta academica. '
            'Ainda nao encontrei notas suficientes para apontar as menores medias com seguranca.'
        )
    prioritized = sorted(averages, key=lambda item: (item[1], item[0]))[:4]
    lines = [f'Os componentes em que {student_name} aparece com as menores medias agora sao:']
    for subject_name, value in prioritized:
        lines.append(f'- {subject_name}: media parcial {value:.1f}'.replace('.', ','))
    return '\n'.join(lines)


def _compose_academic_difficulty_answer(summary: dict[str, Any], *, student_name: str) -> str:
    averages = sorted(_academic_subject_averages(summary), key=lambda item: (item[1], item[0]))
    if not averages:
        return (
            f'Ainda nao encontrei notas suficientes de {student_name} para apontar com seguranca '
            'qual disciplina esta mais dificil neste momento.'
        )
    subject_name, value = averages[0]
    value_text = f'{value:.1f}'.replace('.', ',')
    trailing = ', '.join(f'{name} {grade:.1f}'.replace('.', ',') for name, grade in averages[1:3])
    answer = (
        f'Hoje, a disciplina em que {student_name} aparece com a menor media parcial e {subject_name}, '
        f'com {value_text}/10.'
    )
    if trailing:
        answer += f' Na sequencia aparecem {trailing}.'
    return answer


def _compose_family_upcoming_assessments_answer(
    summaries: list[tuple[str, dict[str, Any], dict[str, Any]]],
) -> str:
    if not summaries:
        return 'Nao encontrei proximas avaliacoes consolidadas das contas vinculadas neste recorte.'
    lines = ['Proximas avaliacoes das contas vinculadas:']
    for student_name, academic_summary, upcoming_summary in summaries:
        class_name = (
            str(academic_summary.get('class_name') or 'nao informada').strip() or 'nao informada'
        )
        lines.append(f'- {student_name} ({class_name})')
        for entry in _format_upcoming_assessments(upcoming_summary)[:4]:
            lines.append(f'  {entry}')
    return '\n'.join(lines)


def _compose_finance_aggregate_answer(summaries: list[dict[str, Any]]) -> str:
    if not summaries:
        return 'Nao encontrei resumo financeiro consolidado das contas vinculadas neste recorte.'
    lines = ['Resumo financeiro das contas vinculadas:']
    total_open = 0
    total_overdue = 0
    for summary in summaries:
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        open_count = int(summary.get('open_invoice_count', 0) or 0)
        overdue_count = int(summary.get('overdue_invoice_count', 0) or 0)
        total_open += open_count
        total_overdue += overdue_count
        next_invoice = _select_next_due_invoice(summary, status_filter=None)
        details = [f'{open_count} em aberto', f'{overdue_count} vencida(s)']
        if isinstance(next_invoice, dict):
            details.append(
                'proximo vencimento {due_date} ({amount_due})'.format(
                    due_date=_format_public_date_text(next_invoice.get('due_date')),
                    amount_due=str(next_invoice.get('amount_due', '0.00')).strip() or '0.00',
                )
            )
        next_step = str(summary.get('next_step') or '').strip()
        line = f'- {student_name}: {", ".join(details)}.'
        if next_step:
            line += f' Proximo passo: {next_step}'
        lines.append(line)
    if total_open or total_overdue:
        lines.append(
            f'- Mensalidade: neste recorte, o financeiro mostra {total_open} cobranca(s) em aberto e {total_overdue} vencida(s) nas faturas escolares.'
        )
        lines.append('- Taxa: nao apareceu taxa separada no resumo financeiro desta conta.')
        lines.append(
            '- Atraso: '
            + (
                'ha faturas vencidas que pedem regularizacao imediata.'
                if total_overdue > 0
                else 'nao ha fatura vencida agora; o foco fica nos proximos vencimentos.'
            )
        )
        lines.append(
            '- Desconto: nao apareceu desconto separado nas faturas deste recorte; se existir negociacao comercial, ela precisa ser confirmada com o financeiro.'
        )
    lines.insert(1, f'- Total de faturas em aberto: {total_open}')
    lines.insert(2, f'- Total de faturas vencidas: {total_overdue}')
    if total_overdue > 0:
        lines.append(
            '- Na pratica, o proximo passo e priorizar as vencidas e regularizar o financeiro antes de qualquer novo atendimento sensivel.'
        )
    elif total_open > 0:
        lines.append(
            '- Na pratica, hoje nao ha bloqueio por atraso vencido; o proximo passo e acompanhar os vencimentos mais proximos e manter os comprovantes em dia.'
        )
    else:
        lines.append('- Na pratica, nao ha pendencia financeira aberta neste recorte.')
    return '\n'.join(lines)


def _compose_family_next_due_answer(summaries: list[dict[str, Any]]) -> str | None:
    candidates: list[tuple[str, dict[str, Any]]] = []
    for summary in summaries:
        if not isinstance(summary, dict):
            continue
        next_invoice = _select_next_due_invoice(summary, status_filter=None)
        if not isinstance(next_invoice, dict):
            continue
        student_name = str(summary.get('student_name') or 'Aluno').strip() or 'Aluno'
        candidates.append((student_name, next_invoice))
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            str(item[1].get('status', '')).lower() not in {'open', 'overdue'},
            str(item[1].get('due_date', '') or '9999-99-99'),
            str(item[0]).lower(),
        )
    )
    student_name, invoice = candidates[0]
    reference_month = str(invoice.get('reference_month', '') or '---').strip()
    due_date = _format_public_date_text(invoice.get('due_date'))
    amount_due = str(invoice.get('amount_due', '0.00')).strip() or '0.00'
    status_label = _humanize_invoice_status(str(invoice.get('status', 'desconhecido')))
    return (
        'O proximo vencimento mais imediato no recorte da familia hoje '
        f'e de {student_name}, na referencia {reference_month}, com vencimento em {due_date} '
        f'e valor {amount_due}. Status atual: {status_label}.'
    )


def _compose_admin_finance_combined_answer(
    *,
    admin_summary: dict[str, Any] | None,
    finance_summaries: list[dict[str, Any]],
    requested_admin_attribute: str | None,
) -> str | None:
    lines: list[str] = []
    has_admin_block = isinstance(admin_summary, dict) and str(
        admin_summary.get('overall_status', '')
    ).strip().lower() in {
        'pending',
        'review',
        'missing',
        'incomplete',
    }
    has_finance_block = any(
        int(summary.get('overdue_invoice_count', 0) or 0) > 0 for summary in finance_summaries
    )
    if has_admin_block:
        lines.append('Hoje ainda existe bloqueio administrativo ou documental neste recorte.')
    elif has_finance_block:
        lines.append('Hoje existe bloqueio financeiro por atraso vencido neste recorte.')
    elif admin_summary or finance_summaries:
        lines.append('Hoje nao ha bloqueio administrativo ou financeiro neste recorte.')
    if isinstance(admin_summary, dict):
        lines.append('Cadastro e documentacao:')
        lines.extend(
            _format_administrative_status(
                admin_summary,
                profile_update=False,
                requested_attribute=requested_admin_attribute,
            )
        )
    if finance_summaries:
        if lines:
            lines.append('')
        lines.append('Financeiro:')
        for line in _compose_finance_aggregate_answer(finance_summaries).splitlines():
            if line.strip():
                lines.append(line)
    return '\n'.join(lines) if lines else None


def _compose_admin_finance_block_status_answer(
    *,
    admin_summary: dict[str, Any] | None,
    finance_summaries: list[dict[str, Any]],
) -> str | None:
    has_admin_block = isinstance(admin_summary, dict) and str(
        admin_summary.get('overall_status', '')
    ).strip().lower() in {
        'pending',
        'review',
        'missing',
        'incomplete',
    }
    has_finance_block = any(
        int(summary.get('overdue_invoice_count', 0) or 0) > 0 for summary in finance_summaries
    )
    if has_admin_block:
        return 'Hoje ainda existe bloqueio administrativo ou documental neste recorte.'
    if has_finance_block:
        return 'Hoje existe bloqueio financeiro por atraso vencido neste recorte.'
    if admin_summary or finance_summaries:
        return 'Hoje nao ha bloqueio administrativo ou financeiro neste recorte.'
    return None


def _format_invoices(summary: dict[str, Any]) -> list[str]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list) or not invoices:
        return ['- Nenhuma fatura encontrada para o contrato atual.']
    lines = []
    for invoice in invoices[:4]:
        if not isinstance(invoice, dict):
            continue
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=invoice.get('status', 'desconhecido'),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines or ['- Nenhuma fatura encontrada para o contrato atual.']


def _filter_invoice_rows(
    summary: dict[str, Any], *, status_filter: set[str] | None
) -> list[dict[str, Any]]:
    invoices = summary.get('invoices')
    if not isinstance(invoices, list):
        return []
    if not status_filter:
        return [invoice for invoice in invoices if isinstance(invoice, dict)]
    filtered: list[dict[str, Any]] = []
    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue
        status = str(invoice.get('status', '')).lower()
        if status in status_filter:
            filtered.append(invoice)
    return filtered


def _detect_finance_status_filter(message: str) -> set[str] | None:
    lowered = _normalize_text(message)
    if any(_message_matches_term(lowered, term) for term in FINANCE_NEXT_DUE_TERMS):
        return None
    if any(term in lowered for term in FINANCE_OVERDUE_TERMS):
        return {'overdue'}
    if any(term in lowered for term in FINANCE_PAID_TERMS):
        return {'paid'}
    if any(term in lowered for term in FINANCE_OPEN_TERMS):
        return {'open', 'overdue'}
    return None


def _wants_finance_count_summary(message: str) -> bool:
    normalized = _normalize_text(message)
    return any(
        _message_matches_term(normalized, term)
        for term in {'quantas', 'quantos', 'qtd', 'quantidade', 'tenho quantas', 'tenho quantos'}
    )


def _wants_upcoming_assessments(message: str) -> bool:
    normalized = _normalize_text(message)
    return _contains_any(message, UPCOMING_ASSESSMENT_TERMS) or any(
        _message_matches_term(normalized, term)
        for term in {
            'proximas provas',
            'próximas provas',
            'provas e entregas',
            'entregas',
        }
    )


def _wants_attendance_timeline(message: str) -> bool:
    normalized = _normalize_text(message)
    if _contains_any(message, ATTENDANCE_TIMELINE_TERMS):
        return True
    return any(
        _message_matches_term(normalized, term)
        for term in {'faltas recentes', 'ausencias recentes', 'ausências recentes'}
    )


def _looks_like_family_finance_aggregate_query(message: str) -> bool:
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in FAMILY_FINANCE_AGGREGATE_TERMS):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'meu financeiro',
            'quero ver meu financeiro',
            'quero ver o meu financeiro',
            'me mostra meu financeiro',
            'mostrar meu financeiro',
            'ver meu financeiro',
        }
    ):
        return True
    if any(
        _message_matches_term(normalized, term)
        for term in {
            'minha situacao financeira',
            'minha situação financeira',
            'situacao financeira como se eu fosse leigo',
            'situação financeira como se eu fosse leigo',
            'separando mensalidade',
            'separando mensalidade, taxa, atraso e desconto',
            'separando mensalidade taxa atraso e desconto',
        }
    ) and any(_message_matches_term(normalized, term) for term in FAMILY_REFERENCE_TERMS):
        return True
    if any(_message_matches_term(normalized, term) for term in FAMILY_REFERENCE_TERMS) and any(
        _message_matches_term(normalized, term)
        for term in {
            'taxa',
            'atraso',
            'atrasos',
            'desconto',
            'descontos',
            'negociar o restante',
            'mensalidade parcialmente paga',
            'o que ja aparece',
            'o que já aparece',
        }
    ):
        return True
    return any(_message_matches_term(normalized, term) for term in FAMILY_REFERENCE_TERMS) and (
        any(_message_matches_term(normalized, term) for term in FINANCE_TERMS)
        or any(
            _message_matches_term(normalized, term)
            for term in {'vencimentos', 'atrasos', 'proximos passos', 'próximos passos'}
        )
    )


def _looks_like_family_attendance_aggregate_query(message: str) -> bool:
    normalized = _normalize_text(message)
    explicit_terms = {
        'resumo de frequencia dos meus dois filhos',
        'resumo de frequência dos meus dois filhos',
        'resumo de frequencia dos meus filhos',
        'resumo de frequência dos meus filhos',
        'panorama de faltas e frequencia',
        'panorama de faltas e frequência',
        'faltas e frequencia dos meus filhos',
        'faltas e frequência dos meus filhos',
        'frequencia dos meus filhos',
        'frequência dos meus filhos',
        'frequencia dos meus dois filhos',
        'frequência dos meus dois filhos',
        'frequencia dos alunos vinculados',
        'frequência dos alunos vinculados',
        'quem exige maior atencao agora',
        'quem exige maior atenção agora',
        'quem exige mais atencao agora',
        'quem exige mais atenção agora',
        'quem inspira mais atencao',
        'quem inspira mais atenção',
        'principal alerta de frequencia dos meus filhos',
        'principal alerta de frequência dos meus filhos',
    }
    if any(_message_matches_term(normalized, term) for term in explicit_terms):
        return True
    has_family_anchor = any(
        _message_matches_term(normalized, term) for term in FAMILY_REFERENCE_TERMS
    ) or any(
        _message_matches_term(normalized, term)
        for term in {'meus dois filhos', 'dos meus dois filhos', 'meus filhos'}
    )
    has_attendance_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'frequencia',
            'frequência',
            'faltas',
            'falta',
            'atrasos',
            'presenca',
            'presença',
            'ausencias',
            'ausências',
        }
    )
    has_explicit_academic_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'componente',
            'componentes',
            'disciplina',
            'disciplinas',
            'materia',
            'materias',
            'nota',
            'notas',
            'media',
            'média',
            'academico',
            'acadêmico',
        }
    )
    has_explicit_finance_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'financeiro',
            'financeira',
            'situacao financeira',
            'situação financeira',
            'mensalidade',
            'mensalidades',
            'boleto',
            'boletos',
            'fatura',
            'faturas',
            'pagamento',
            'pagamentos',
            'vencimento',
            'vencimentos',
            'proximos passos',
            'próximos passos',
            'comprovantes',
        }
    )
    has_non_ambiguous_attendance_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'frequencia',
            'frequência',
            'faltas',
            'falta',
            'presenca',
            'presença',
            'ausencias',
            'ausências',
        }
    )
    has_attention_focus = any(
        _message_matches_term(normalized, term)
        for term in {
            'quem inspira mais atencao',
            'quem inspira mais atenção',
            'quem exige maior atencao',
            'quem exige maior atenção',
            'quem exige mais atencao',
            'quem exige mais atenção',
            'maior atencao',
            'maior atenção',
            'mais atencao',
            'mais atenção',
            'principal alerta',
        }
    )
    if has_explicit_academic_focus and not has_attendance_focus:
        return False
    if has_explicit_finance_focus and not has_non_ambiguous_attendance_focus:
        return False
    return has_family_anchor and (has_attendance_focus or has_attention_focus)


def _looks_like_family_academic_aggregate_query(message: str) -> bool:
    if _looks_like_family_attendance_aggregate_query(message):
        return False
    normalized = _normalize_text(message)
    if any(_message_matches_term(normalized, term) for term in FAMILY_ACADEMIC_AGGREGATE_TERMS):
        return True
    return any(_message_matches_term(normalized, term) for term in FAMILY_REFERENCE_TERMS) and any(
        _message_matches_term(normalized, term)
        for term in {
            'quadro academico',
            'quadro acadêmico',
            'panorama academico',
            'panorama acadêmico',
            'limite de aprovacao',
            'limite de aprovação',
            'corte de aprovacao',
            'corte de aprovação',
            'componentes',
            'mais vulneravel',
            'mais vulnerável',
            'academicamente pior',
            'mais critico academicamente',
            'mais crítico academicamente',
        }
    )


def _looks_like_family_academic_student_focus_followup(
    actor: dict[str, Any] | None,
    message: str,
    *,
    conversation_context: dict[str, Any] | None = None,
) -> bool:
    if not _recent_multi_student_summary_context(actor, conversation_context=conversation_context):
        return False
    normalized = _normalize_text(message)
    if not _focus_marked_student_from_message(
        _eligible_students(actor, capability='academic'),
        message,
    ):
        return False
    return any(
        _message_matches_term(normalized, term)
        for term in {
            'qual componente',
            'qual disciplina',
            'mais alerta',
            'acende mais alerta',
            'chama mais atencao',
            'chama mais atenção',
            'chamam atencao',
            'chamam atenção',
            'mais fragil',
            'mais frágil',
            'mais vulneravel',
            'mais vulnerável',
            'mais critico',
            'mais crítico',
            'ponto mais fraco',
            'mais claro',
        }
    )


def _mentions_personal_admin_status(message: str) -> bool:
    normalized = _normalize_text(message)
    has_personal_anchor = any(
        _message_matches_term(normalized, term)
        for term in {
            'meu',
            'minha',
            'meus',
            'minhas',
            'estou',
            'cadastro',
            'documentacao',
            'documentação',
            'dados cadastrais',
            'atualizada',
            'atualizado',
            'completa',
            'completo',
            'familia',
            'família',
        }
    )
    return has_personal_anchor and any(
        _message_matches_term(normalized, term) for term in PERSONAL_ADMIN_STATUS_TERMS
    )


def _wants_profile_update_guidance(message: str) -> bool:
    return _contains_any(message, PERSONAL_PROFILE_UPDATE_TERMS)


def _humanize_invoice_status(status: str | None) -> str:
    normalized = _normalize_text(status or '')
    mapping = {
        'paid': 'paga',
        'open': 'em aberto',
        'overdue': 'vencida',
        'cancelled': 'cancelada',
    }
    return mapping.get(normalized, status or 'desconhecido')


def _finance_empty_lines(status_filter: set[str] | None = None) -> list[str]:
    if status_filter == {'paid'}:
        return ['- Nao encontrei faturas pagas neste recorte.']
    if status_filter == {'overdue'}:
        return ['- Hoje nao ha faturas vencidas neste recorte.']
    if status_filter == {'open', 'overdue'}:
        return ['- Hoje nao ha faturas em aberto ou vencidas neste recorte.']
    return ['- Nao encontrei faturas registradas neste recorte.']


def _format_invoice_lines(
    invoices: list[dict[str, Any]],
    *,
    status_filter: set[str] | None = None,
) -> list[str]:
    if not invoices:
        return _finance_empty_lines(status_filter)
    lines = []
    for invoice in invoices[:6]:
        lines.append(
            '- {reference_month}: vencimento {due_date}, status {status}, valor {amount_due}'.format(
                reference_month=invoice.get('reference_month', '---'),
                due_date=invoice.get('due_date', '---'),
                status=_humanize_invoice_status(str(invoice.get('status', 'desconhecido'))),
                amount_due=invoice.get('amount_due', '0.00'),
            )
        )
    return lines


def _parse_invoice_amount(value: Any) -> float:
    raw = str(value or '').strip()
    if not raw:
        return 0.0
    raw = raw.replace('R$', '').replace(' ', '')
    if ',' in raw and '.' in raw:
        raw = raw.replace('.', '').replace(',', '.')
    elif ',' in raw:
        raw = raw.replace(',', '.')
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _format_upcoming_assessments(summary: dict[str, Any]) -> list[str]:
    assessments = summary.get('assessments')
    if not isinstance(assessments, list) or not assessments:
        return ['- Nao encontrei proximas avaliacoes registradas neste recorte.']
    lines = []
    for assessment in assessments[:6]:
        if not isinstance(assessment, dict):
            continue
        lines.append(
            '- {subject_name} - {item_title}: {due_date}'.format(
                subject_name=assessment.get('subject_name', 'Disciplina'),
                item_title=assessment.get('item_title', 'Avaliacao'),
                due_date=assessment.get('due_date', 'data nao informada'),
            )
        )
    return lines or ['- Nao encontrei proximas avaliacoes registradas neste recorte.']


def _format_attendance_timeline(summary: dict[str, Any]) -> list[str]:
    records = summary.get('records')
    if not isinstance(records, list) or not records:
        return ['- Nao encontrei faltas ou registros recentes com data neste recorte.']
    lines = []
    for record in records[:8]:
        if not isinstance(record, dict):
            continue
        status = str(record.get('status', 'nao informado')).lower()
        status_label = {
            'present': 'presenca',
            'late': 'atraso',
            'absent': 'falta',
        }.get(status, status)
        suffix = ''
        minutes_absent = int(record.get('minutes_absent', 0) or 0)
        if minutes_absent > 0:
            suffix = f' ({minutes_absent} min)'
        lines.append(
            '- {record_date} - {subject_name}: {status_label}{suffix}'.format(
                record_date=record.get('record_date', 'data nao informada'),
                subject_name=record.get('subject_name', 'Disciplina'),
                status_label=status_label,
                suffix=suffix,
            )
        )
    return lines or ['- Nao encontrei faltas ou registros recentes com data neste recorte.']


def _format_grade_target_value(value: float) -> str:
    return f'{value:.1f}'.replace('.', ',')


def _subject_label_from_filter(summary: dict[str, Any], subject_filter: str | None) -> str | None:
    if not subject_filter:
        return None
    available_subjects = _available_subjects(summary)
    subject = available_subjects.get(subject_filter)
    if isinstance(subject, dict):
        label = str(subject.get('subject_name', '')).strip()
        if label:
            return label
    return subject_filter.title()


def _compose_grade_requirement_answer(
    summary: dict[str, Any],
    *,
    student_name: str,
    message: str | None,
    conversation_context: dict[str, Any] | None,
) -> str:
    subject_filter = _detect_subject_filter(
        message or '',
        summary,
        conversation_context=conversation_context,
        focus_kind='grades',
    )
    subject_label = _subject_label_from_filter(summary, subject_filter)
    if not subject_filter or not subject_label:
        return (
            f'Para eu te dizer quanto falta para {student_name} atingir a media de aprovacao, '
            'me diga a disciplina. Por exemplo: "em Fisica".'
        )

    filtered_grades = _filter_grade_rows(summary, subject_filter=subject_filter, term_filter=None)
    normalized_scores: list[float] = []
    for item in filtered_grades:
        if not isinstance(item, dict):
            continue
        score = float(item.get('score', 0) or 0)
        max_score = float(item.get('max_score', 0) or 0)
        if max_score <= 0:
            continue
        normalized_scores.append((score / max_score) * 10.0)

    if not normalized_scores:
        return (
            f'Ainda nao encontrei notas lancadas de {student_name} em {subject_label} '
            'para calcular a media parcial.'
        )

    current_average = sum(normalized_scores) / len(normalized_scores)
    gap = max(0.0, PASSING_GRADE_TARGET - current_average)
    average_label = _format_grade_target_value(current_average)
    if gap <= 0:
        return (
            f'Com as notas lancadas ate agora, {student_name} esta com media parcial de '
            f'{average_label}/10 em {subject_label}. '
            'Se a referencia de aprovacao for 7,0, ja esta acima do necessario.'
        )

    gap_label = _format_grade_target_value(gap)
    return (
        f'Com as notas lancadas ate agora, {student_name} esta com media parcial de '
        f'{average_label}/10 em {subject_label}. '
        f'Se a referencia de aprovacao for 7,0, faltam {gap_label} ponto(s) para atingir essa media.'
    )


def _administrative_checklist_lines(summary: dict[str, Any]) -> list[str]:
    checklist = summary.get('checklist')
    if not isinstance(checklist, list) or not checklist:
        return ['- Nao encontrei itens administrativos detalhados para este cadastro.']
    lines: list[str] = []
    for item in checklist:
        if not isinstance(item, dict):
            continue
        label = str(item.get('label', 'Item'))
        status = ADMIN_STATUS_LABELS.get(
            str(item.get('status', '')).lower(), str(item.get('status', 'nao informado'))
        )
        notes = str(item.get('notes', '')).strip()
        line = f'- {label}: {status}'
        if notes:
            line += f'. {notes}'
        lines.append(line)
    return lines or ['- Nao encontrei itens administrativos detalhados para este cadastro.']
