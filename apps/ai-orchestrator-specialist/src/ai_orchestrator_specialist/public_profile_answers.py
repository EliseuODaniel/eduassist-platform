from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from .public_doc_knowledge import compose_public_teacher_directory_boundary
from .public_query_patterns import _extract_teacher_subject


def _normalize_text(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _school_name(profile: dict[str, Any] | None) -> str:
    return str((profile or {}).get("school_name") or "Colegio Horizonte").strip() or "Colegio Horizonte"


def _select_contact_channel(
    profile: dict[str, Any] | None,
    *,
    label_contains: tuple[str, ...] = (),
    channel_equals: tuple[str, ...] = (),
) -> dict[str, Any] | None:
    channels = (profile or {}).get("contact_channels")
    if not isinstance(channels, list):
        return None
    normalized_labels = tuple(_normalize_text(item) for item in label_contains)
    normalized_channels = tuple(_normalize_text(item) for item in channel_equals)
    for item in channels:
        if not isinstance(item, dict):
            continue
        label = _normalize_text(item.get("label"))
        channel = _normalize_text(item.get("channel"))
        if normalized_labels and not any(term in label for term in normalized_labels):
            continue
        if normalized_channels and channel not in normalized_channels:
            continue
        return item
    return None


def _compose_human_handoff_answer(profile: dict[str, Any] | None) -> str:
    secretaria_phone = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("telefone",))
    secretaria_whatsapp = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("whatsapp",))
    secretaria_email = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("email",))
    atendimento_whatsapp = _select_contact_channel(
        profile,
        label_contains=("atendimento comercial",),
        channel_equals=("whatsapp",),
    )
    parts = [
        "Se voce quer falar com atendimento humano agora, estes sao os canais mais diretos do Colegio Horizonte:",
    ]
    if secretaria_phone:
        parts.append(f"- Secretaria por telefone: {secretaria_phone.get('value')}")
    if secretaria_whatsapp:
        parts.append(f"- Secretaria digital por WhatsApp: {secretaria_whatsapp.get('value')}")
    elif atendimento_whatsapp:
        parts.append(f"- Atendimento comercial por WhatsApp: {atendimento_whatsapp.get('value')}")
    if secretaria_email:
        parts.append(f"- Secretaria por email: {secretaria_email.get('value')}")
    parts.append("Se quiser, eu tambem posso abrir um pedido por aqui para a equipe acompanhar seu caso.")
    return "\n".join(parts)


def _compose_support_process_boundary_answer() -> str:
    return (
        "Hoje eu trato esses tres fluxos de forma diferente: protocolo registra uma solicitacao institucional rastreavel; "
        "chamado costuma ser o ticket operacional associado ao atendimento; e handoff humano e o encaminhamento real para uma fila ou equipe, "
        "normalmente com protocolo e status para acompanhamento."
    )


def _compose_service_routing_fast_answer(profile: dict[str, Any] | None, message: str) -> str | None:
    catalog = (profile or {}).get("service_catalog")
    if not isinstance(catalog, list):
        return None
    index = {
        str(item.get("service_key") or "").strip(): item
        for item in catalog
        if isinstance(item, dict) and str(item.get("service_key") or "").strip()
    }
    normalized = _normalize_text(message)
    requested: list[tuple[str, str]] = []
    if any(
        term in normalized
        for term in {"bolsa", "bolsas", "desconto", "descontos", "matricula", "matrícula", "atendimento comercial", "admissoes", "admissao"}
    ):
        requested.append(("atendimento_admissoes", "Atendimento comercial / Admissoes"))
    if any(term in normalized for term in {"boleto", "boletos", "financeiro", "fatura", "mensalidade"}):
        requested.append(("financeiro_escolar", "Financeiro"))
    if any(term in normalized for term in {"bullying", "orientacao", "orientação", "socioemocional", "convivencia", "convivência"}):
        requested.append(("orientacao_educacional", "Orientacao educacional"))
    if any(term in normalized for term in {"direcao", "direção", "diretora", "diretor"}):
        requested.append(("solicitacao_direcao", "Direcao"))
    if any(
        term in normalized
        for term in {"trabalhar ai", "trabalhar aí", "quero trabalhar", "vaga", "vagas", "curriculo", "currículo", "professor"}
    ):
        requested.append(("carreiras_docentes", "Carreiras docentes"))
    if not requested:
        return None
    wants_one_line_per_sector = any(
        term in normalized
        for term in {
            "uma linha por setor",
            "sem explicar o resto da escola",
            "nao me manda menu geral",
            "não me manda menu geral",
            "caminho mais curto",
            "nao a lista completa",
            "não a lista completa",
        }
    )
    wants_priority = any(
        term in normalized
        for term in {
            "entra primeiro",
            "qual desses setores entra primeiro",
            "quem entra primeiro",
            "setor entra primeiro",
        }
    )
    has_documental_pending = any(
        term in normalized
        for term in {
            "documento pendente",
            "documentacao pendente",
            "documentação pendente",
            "pendencia documental",
            "pendência documental",
        }
    )
    lines: list[str] = []
    direct_order: list[str] = []
    one_line_lines: list[str] = []
    if any(term in normalized for term in {"direcao", "direção", "diretora", "diretor"}):
        leadership = (profile or {}).get("leadership_team")
        if isinstance(leadership, list):
            first = next((item for item in leadership if isinstance(item, dict)), None)
            if isinstance(first, dict):
                title = str(first.get("title") or "Direcao geral").strip()
                name = str(first.get("name") or "").strip()
                channel = str(first.get("contact_channel") or "").strip()
                if name and channel:
                    lines.append(f"- {title}: {name}. Canal institucional: {channel}.")
                    direct_order.append("Direcao")
                    compact_line = f"- Direcao: {channel}."
                    if compact_line not in one_line_lines:
                        one_line_lines.append(compact_line)
                elif name:
                    lines.append(f"- {title}: {name}.")
                    direct_order.append("Direcao")
                    compact_line = f"- Direcao: {name}."
                    if compact_line not in one_line_lines:
                        one_line_lines.append(compact_line)
    for service_key, label in requested:
        item = index.get(service_key)
        if not isinstance(item, dict):
            continue
        request_channel = str(item.get("request_channel") or "canal institucional").strip()
        lines.append(f"- {label}: {request_channel}.")
        direct_order.append(label)
        compact_label = label
        if wants_one_line_per_sector and service_key == "atendimento_admissoes":
            compact_label = "Bolsas / admissoes"
        compact_line = f"- {compact_label}: {request_channel}."
        if service_key == "solicitacao_direcao" and any(line.startswith("- Direcao:") for line in one_line_lines):
            continue
        if compact_line not in one_line_lines:
            one_line_lines.append(compact_line)
    if not lines:
        return None
    if wants_priority:
        if any("Atendimento comercial / Admissoes" == label for label in direct_order) and has_documental_pending:
            return (
                "Se o tema for bolsa com documento pendente, o primeiro setor que entra e "
                "Atendimento comercial / Admissoes. Depois, se houver impacto em contrato ou cobranca, entra o "
                "Financeiro. A Direcao fica como escalonamento institucional se o caso sair da rotina normal."
            )
        first_sector = direct_order[0] if direct_order else "o canal institucional principal"
        return f"Desses setores, o primeiro passo hoje e {first_sector}."
    if wants_one_line_per_sector:
        compact_lines = one_line_lines or lines
        compact_items = [line[2:].strip() if line.startswith("- ") else line.strip() for line in compact_lines]
        return " | ".join(item for item in compact_items if item)
    return "Hoje estes sao os responsaveis e canais mais diretos por assunto:\n" + "\n".join(lines)


def _compose_public_teacher_directory_answer(profile: dict[str, Any] | None, message: str) -> str | None:
    subject = _extract_teacher_subject(message)
    if subject:
        school_name = _school_name(profile)
        return (
            f"O {school_name} nao divulga nomes nem contatos diretos de professores por disciplina, como {subject}. "
            "Se quiser, eu posso te indicar a coordenacao pedagogica ou o setor certo para seguir com isso."
        )
    return compose_public_teacher_directory_boundary(profile)


def _compose_contact_bundle_answer(profile: dict[str, Any] | None, *, message: str | None = None) -> str | None:
    if not isinstance(profile, dict):
        return None
    normalized = _normalize_text(message)
    address_line = str(profile.get("address_line") or "").strip()
    district = str(profile.get("district") or "").strip()
    city = str(profile.get("city") or "").strip()
    state = str(profile.get("state") or "").strip()
    postal_code = str(profile.get("postal_code") or "").strip()
    phone = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("telefone",))
    secretaria_whatsapp = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("whatsapp",))
    secretaria_email = _select_contact_channel(profile, label_contains=("secretaria",), channel_equals=("email",))
    financeiro_phone = _select_contact_channel(profile, label_contains=("financeiro",), channel_equals=("telefone",))
    financeiro_whatsapp = _select_contact_channel(profile, label_contains=("financeiro",), channel_equals=("whatsapp",))
    financeiro_email = _select_contact_channel(profile, label_contains=("financeiro",), channel_equals=("email",))
    if not address_line and not phone and not secretaria_whatsapp and not secretaria_email:
        return None
    locality = ", ".join(part for part in [address_line, district, city, state] if part)
    if locality and postal_code:
        locality = f"{locality}, CEP {postal_code}"
    parts: list[str] = []
    if locality:
        parts.append(f"O endereco completo da escola hoje e {locality}.")
    if phone:
        parts.append(f"O telefone principal e {phone.get('value')}.")
    if secretaria_whatsapp:
        parts.append(f"O melhor canal para a secretaria hoje e o WhatsApp {secretaria_whatsapp.get('value')}.")
    elif secretaria_email:
        parts.append(f"O melhor canal para a secretaria hoje e o email {secretaria_email.get('value')}.")
    if any(term in normalized for term in {"financeiro", "mensalidade", "boleto", "fatura"}):
        if financeiro_whatsapp:
            parts.append(f"O melhor canal para o financeiro hoje e o WhatsApp {financeiro_whatsapp.get('value')}.")
        elif financeiro_email:
            parts.append(f"O melhor canal para o financeiro hoje e o email {financeiro_email.get('value')}.")
        elif financeiro_phone:
            parts.append(f"O telefone mais direto do financeiro hoje e {financeiro_phone.get('value')}.")
    return " ".join(parts) if parts else None


def _timeline_entry(entries: list[dict[str, Any]], *, topic_fragment: str) -> dict[str, Any] | None:
    for item in entries:
        if not isinstance(item, dict):
            continue
        if topic_fragment in str(item.get("topic_key") or ""):
            return item
    return None


def _timeline_event_date(item: dict[str, Any] | None) -> str:
    if not isinstance(item, dict):
        return ""
    return str(item.get("event_date") or item.get("starts_at") or "").strip()


def _compose_timeline_bundle_answer(
    profile: dict[str, Any] | None,
    message: str,
    *,
    recent_user_messages: list[str] | None = None,
) -> str | None:
    entries = (profile or {}).get("public_timeline")
    if not isinstance(entries, list):
        return None
    normalized = _normalize_text(message)
    wants_enrollment = "matricula" in normalized or "matrícula" in normalized
    wants_classes = any(
        term in normalized
        for term in {
            "comecam as aulas",
            "começam as aulas",
            "comeco das aulas",
            "começo das aulas",
            "inicio das aulas",
            "início das aulas",
            "ano letivo",
        }
    )
    wants_family = any(term in normalized for term in {"responsaveis", "responsáveis", "reuniao", "reunião", "familia", "família"})
    asks_before_after = any(
        term in normalized
        for term in {"antes ou depois", "antes das aulas", "depois das aulas", "primeira reuniao", "primeira reunião"}
    )
    asks_order_only = any(
        term in normalized
        for term in {"so esse recorte", "só esse recorte", "nao quero o calendario inteiro", "não quero o calendário inteiro", "recorte em ordem"}
    )
    wants_assessments = any(
        term in normalized
        for term in {"avaliac", "prova", "provas", "simulado", "simulados"}
    )
    normalized_recent = " ".join(_normalize_text(item) for item in (recent_user_messages or []))
    recent_has_timeline_context = any(
        term in normalized_recent
        for term in {
            "matricula",
            "matrícula",
            "inicio das aulas",
            "início das aulas",
            "ano letivo",
            "reuniao de responsaveis",
            "reunião de responsáveis",
        }
    )
    if asks_before_after:
        wants_enrollment = True
        wants_classes = True
        wants_family = True
    if asks_order_only:
        wants_enrollment = True
        wants_classes = True
        wants_family = True
    if recent_has_timeline_context and asks_before_after:
        wants_enrollment = True
        wants_classes = True
        wants_family = True
    if recent_has_timeline_context and asks_order_only:
        wants_enrollment = True
        wants_classes = True
        wants_family = True
    if (
        not (wants_enrollment and wants_classes)
        and any(term in normalized for term in {"depois disso", "proximo marco", "próximo marco"})
        and wants_family
        and any(term in normalized_recent for term in {"portal", "documentos", "secretaria", "matricula", "matrícula", "inicio das aulas", "início das aulas"})
    ):
        wants_enrollment = True
        wants_classes = True
    if not (wants_enrollment and wants_classes):
        return None
    admissions_item = _timeline_entry(entries, topic_fragment="admissions_opening")
    school_year_item = _timeline_entry(entries, topic_fragment="school_year_start")
    family_item = _timeline_entry(entries, topic_fragment="family_meeting")
    if (
        wants_family
        and asks_before_after
        and isinstance(school_year_item, dict)
        and isinstance(family_item, dict)
    ):
        school_year_date = _timeline_event_date(school_year_item)
        family_date = _timeline_event_date(family_item)
        if school_year_date and family_date:
            ordering = "depois" if family_date >= school_year_date else "antes"
            family_summary = str(family_item.get("summary") or "").strip()
            school_year_summary = str(school_year_item.get("summary") or "").strip()
            return (
                f"A primeira reuniao com responsaveis acontece {ordering} do inicio das aulas. "
                f"Inicio das aulas: {school_year_summary} "
                f"Primeira reuniao: {family_summary}"
            ).strip()
    lines: list[str] = []
    topics = ["admissions_opening", "school_year_start"]
    if wants_family:
        topics.append("family_meeting")
    for topic in topics:
        item = _timeline_entry(entries, topic_fragment=topic)
        if not isinstance(item, dict):
            continue
        summary = str(item.get("summary") or "").strip()
        notes = str(item.get("notes") or "").strip()
        line = f"{summary} {notes}".strip()
        if line:
            lines.append(line)
    if lines and any(term in normalized for term in {"ordem", "sequencia", "sequência", "recorte"}):
        ordered_lines = []
        labels = [
            "1) Matricula e ingresso",
            "2) Inicio das aulas",
            "3) Reuniao com responsaveis",
        ]
        for label, line in zip(labels, lines, strict=False):
            ordered_lines.append(f"{label}: {line}")
        return "\n".join(ordered_lines)
    if lines:
        if wants_assessments:
            lines.append(
                "No calendario publico, primeiro entra a matricula, depois comecam as aulas e, nas primeiras semanas, a agenda de avaliacoes passa a organizar o inicio do ano junto com a reuniao inicial das familias."
            )
        else:
            lines.append(
                "Na pratica, primeiro entra a matricula, depois comecam as aulas e, na sequencia, vem a reuniao inicial com as familias."
            )
    return "\n".join(lines) if lines else None


def _compose_policy_compare_answer(profile: dict[str, Any] | None) -> str | None:
    policy = (profile or {}).get("academic_policy")
    if not isinstance(policy, dict):
        return None
    attendance = policy.get("attendance_policy")
    passing = policy.get("passing_policy")
    minimum = ""
    average = ""
    if isinstance(attendance, dict):
        minimum = str(attendance.get("minimum_attendance_percent") or "").strip().replace(".", ",")
    if isinstance(passing, dict):
        average = str(passing.get("passing_average") or "").strip().replace(".", ",")
    attendance_line = (
        f"O manual de regulamentos gerais organiza convivencia, frequencia e rotina, com referencia minima de {minimum}% de presenca por componente."
        if minimum
        else "O manual de regulamentos gerais organiza convivencia, frequencia e rotina escolar."
    )
    passing_line = (
        f"Ja a politica de avaliacao detalha aprovacao, media {average}, recuperacao, monitorias e criterios de promocao."
        if average
        else "Ja a politica de avaliacao detalha aprovacao, recuperacao, monitorias e criterios de promocao."
    )
    closing = (
        "Na pratica, primeiro o manual ajuda a entender convivencia, frequencia e rotina; "
        "depois a politica academica orienta segunda chamada, recuperacao e aprovacao; "
        "e o proximo passo, se houver duvida operacional, e confirmar isso pelo canal oficial da secretaria ou da coordenacao."
    )
    return " ".join((attendance_line, passing_line, closing))


def _compose_service_credentials_bundle_answer(profile: dict[str, Any] | None) -> str:
    warning = ""
    document_policy = (profile or {}).get("document_submission_policy")
    if isinstance(document_policy, dict):
        warning = str(document_policy.get("warning") or "").strip()
    lines = [
        "Hoje a familia precisa entender quatro frentes publicas deste fluxo:",
        "- Secretaria: recebe declaracoes, historico, atualizacoes cadastrais e orientacoes administrativas.",
        "- Portal institucional: centraliza protocolo e envio digital inicial de documentos.",
        "- Credenciais: login e senha do portal continuam sendo a base de acesso; se voce perder o acesso, o melhor caminho e a secretaria ou o suporte digital.",
        "- Documentos: o envio inicial pode ser feito por portal institucional, email da secretaria ou secretaria presencial.",
    ]
    if warning:
        lines.append(warning)
    return "\n".join(lines)


def _extract_requested_visit_date_iso(message: str) -> str | None:
    normalized = _normalize_text(message)
    explicit_match = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", normalized)
    if explicit_match:
        day = int(explicit_match.group(1))
        month = int(explicit_match.group(2))
        year_raw = explicit_match.group(3)
        year = date.today().year if year_raw is None else int(year_raw)
        if year < 100:
            year += 2000
        try:
            return date(year, month, day).isoformat()
        except ValueError:
            return None
    weekday_map = {
        "segunda": 0,
        "terca": 1,
        "terça": 1,
        "quarta": 2,
        "quinta": 3,
        "sexta": 4,
        "sabado": 5,
        "sábado": 5,
    }
    today = date.today()
    for label, weekday in weekday_map.items():
        if label not in normalized:
            continue
        offset = (weekday - today.weekday()) % 7
        if offset == 0:
            offset = 7
        return (today + timedelta(days=offset)).isoformat()
    return None


def _extract_requested_visit_window(profile: dict[str, Any] | None, message: str) -> str | None:
    normalized = _normalize_text(message)
    time_match = re.search(r"\b(\d{1,2})(?:[:h](\d{2}))\b", normalized)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        return f"{hour:02d}:{minute:02d}"
    offers = (profile or {}).get("visit_offers")
    if isinstance(offers, list):
        for item in offers:
            if not isinstance(item, dict):
                continue
            day_label = _normalize_text(item.get("day_label"))
            if "quinta" in normalized and "quinta" not in day_label:
                continue
            if "terca" in normalized and "terça" not in day_label and "terca" not in day_label:
                continue
            if "tarde" in normalized and any(term in day_label for term in {"quinta", "tarde"}):
                start_time = str(item.get("start_time") or "").strip()
                if start_time:
                    return start_time
            if "manha" in normalized and any(term in day_label for term in {"terça", "terca", "manha"}):
                start_time = str(item.get("start_time") or "").strip()
                if start_time:
                    return start_time
    if "manha" in normalized:
        return "09:00"
    if "tarde" in normalized:
        return "14:30"
    if "noite" in normalized:
        return "18:30"
    return None


def _weekday_label_from_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        resolved = date.fromisoformat(value)
    except ValueError:
        return None
    labels = [
        "segunda-feira",
        "terca-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sabado",
        "domingo",
    ]
    return labels[resolved.weekday()]


def _feature_note(profile: dict[str, Any] | None, *, name_hint: str) -> str | None:
    inventory = profile.get("feature_inventory") if isinstance(profile, dict) else None
    if not isinstance(inventory, list):
        return None
    normalized_hint = _normalize_text(name_hint)
    for item in inventory:
        if not isinstance(item, dict):
            continue
        title_candidates = [
            _normalize_text(item.get("name")),
            _normalize_text(item.get("label")),
            _normalize_text(item.get("feature_key")),
        ]
        if normalized_hint and any(normalized_hint in title for title in title_candidates if title):
            note = str(item.get("notes", "") or "").strip()
            if note:
                return note
    return None


def _feature_label(profile: dict[str, Any] | None, *, name_hint: str) -> str | None:
    inventory = profile.get("feature_inventory") if isinstance(profile, dict) else None
    if not isinstance(inventory, list):
        return None
    normalized_hint = _normalize_text(name_hint)
    for item in inventory:
        if not isinstance(item, dict):
            continue
        title_candidates = [
            _normalize_text(item.get("name")),
            _normalize_text(item.get("label")),
            _normalize_text(item.get("feature_key")),
        ]
        if normalized_hint and any(normalized_hint in title for title in title_candidates if title):
            label = str(item.get("label") or item.get("name") or "").strip()
            if label:
                return label
    return None


def _compose_public_pedagogical_answer(profile: dict[str, Any]) -> str | None:
    education_model = str(profile.get("education_model", "") or "").strip()
    curriculum_basis = str(profile.get("curriculum_basis", "") or "").strip()
    short_headline = str(profile.get("short_headline", "") or "").strip()
    if not any((education_model, curriculum_basis, short_headline)):
        return None
    parts: list[str] = []
    if education_model:
        parts.append(f"A proposta pedagogica publicada hoje combina {education_model}.")
    if curriculum_basis:
        parts.append(f"No Ensino Medio, isso aparece junto de {curriculum_basis}.")
    if short_headline:
        parts.append(short_headline)
    parts.append(
        "Na pratica, isso aparece em acompanhamento mais proximo da aprendizagem, projeto de vida e uma rotina pedagogica mais explicita no dia a dia."
    )
    return " ".join(part for part in parts if part).strip()


def _compose_public_pitch_answer(profile: dict[str, Any] | None) -> str | None:
    pedagogical = _compose_public_pedagogical_answer(profile or {})
    if not pedagogical:
        return None
    return (
        "Se eu tivesse 30 segundos para resumir esta escola, eu diria isto: "
        "ela combina aprendizagem por projetos, acompanhamento mais proximo e trilhas academicas no contraturno. "
        f"{pedagogical}"
    )


def _compose_public_attendance_hours_answer(profile: dict[str, Any] | None) -> str | None:
    shift_offers = (profile or {}).get("shift_offers")
    if not isinstance(shift_offers, list):
        return None
    lines = ["Hoje o Colegio Horizonte funciona nestes horarios letivos publicos:"]
    for row in shift_offers[:3]:
        if not isinstance(row, dict):
            continue
        segment = str(row.get("segment") or "segmento").strip()
        shift = str(row.get("shift_label") or "").strip()
        starts = str(row.get("starts_at") or "--").strip()
        ends = str(row.get("ends_at") or "--").strip()
        lines.append(f"- {segment} ({shift}): {starts} as {ends}.")
    library = _feature_note(profile, name_hint="biblioteca")
    if library:
        lines.append(f"- Biblioteca Aurora: {library}")
    return "\n".join(lines)


def _compose_shift_offers_answer(profile: dict[str, Any] | None, *, message: str) -> str | None:
    rows = (profile or {}).get("shift_offers")
    if not isinstance(rows, list) or not rows:
        return None
    normalized = _normalize_text(message)
    rendered_rows: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        segment = str(row.get("segment") or "").strip()
        shift_label = str(row.get("shift_label") or "").strip()
        starts_at = str(row.get("starts_at") or "").strip()
        ends_at = str(row.get("ends_at") or "").strip()
        notes = str(row.get("notes") or "").strip()
        if not segment or not shift_label:
            continue
        rendered_rows.append(
            {
                "segment": segment,
                "shift_label": shift_label,
                "starts_at": starts_at,
                "ends_at": ends_at,
                "notes": notes,
            }
        )
    if not rendered_rows:
        return None
    requested_segment: str | None = None
    if "ensino medio" in normalized or "ensino médio" in normalized:
        requested_segment = "medio"
    elif "fundamental" in normalized:
        requested_segment = "fundamental"
    selected = [
        row for row in rendered_rows if requested_segment is None or requested_segment in _normalize_text(row["segment"])
    ]
    if not selected:
        selected = rendered_rows
    lines = ["Hoje o Colegio Horizonte publica estes turnos de atendimento escolar:"]
    for row in selected:
        lines.append(f"- {row['segment']}: {row['shift_label']} ({row['starts_at']} as {row['ends_at']}).")
    offered_shift_labels = {_normalize_text(row["shift_label"]) for row in rendered_rows}
    asked_about_contrast = any(term in normalized for term in {"matutivo", "matutino", "vespertino", "noturno"})
    if asked_about_contrast:
        missing: list[str] = []
        if all(term not in offered_shift_labels for term in {"manha", "manhã"}):
            missing.append("matutino")
        if "vespertino" in normalized and "vespertino" not in offered_shift_labels and "tarde" not in offered_shift_labels:
            missing.append("vespertino regular")
        if "noturno" in normalized and "noturno" not in offered_shift_labels:
            missing.append("noturno regular")
        if missing:
            rendered_missing = ", ".join(missing)
            lines.append(f"Nos canais publicos atuais, nao encontrei oferta regular de {rendered_missing}.")
    return "\n".join(lines)


def _compose_interval_schedule_answer(profile: dict[str, Any] | None, *, message: str) -> str | None:
    rows = (profile or {}).get("interval_schedule")
    if not isinstance(rows, list) or not rows:
        return (
            "Hoje eu nao encontrei nos canais publicos da escola um quadro oficial de horarios de intervalo. "
            "Se quiser, eu posso te indicar a coordenacao ou a secretaria para confirmar esse detalhe."
        )
    normalized = _normalize_text(message)
    requested_segment: str | None = None
    if "ensino medio" in normalized or "ensino médio" in normalized:
        requested_segment = "medio"
    elif "fundamental" in normalized:
        requested_segment = "fundamental"
    selected: list[dict[str, Any]] = [
        row
        for row in rows
        if isinstance(row, dict) and (requested_segment is None or requested_segment in _normalize_text(row.get("segment")))
    ]
    if not selected:
        selected = [row for row in rows if isinstance(row, dict)]
    if not selected:
        return None
    lines = ["Nos canais publicos do Colegio Horizonte, os horarios de intervalo sao:"]
    for row in selected[:4]:
        segment = str(row.get("segment") or "segmento").strip()
        label = str(row.get("label") or "Intervalo").strip()
        starts_at = str(row.get("starts_at") or "--").strip()
        ends_at = str(row.get("ends_at") or "--").strip()
        notes = str(row.get("notes") or "").strip()
        lines.append(f"- {segment} ({label}): {starts_at} as {ends_at}.")
        if notes:
            lines.append(f"  {notes}")
    return "\n".join(lines)


def _compose_curriculum_components_answer(profile: dict[str, Any] | None, *, segment_hint: str | None = None) -> str | None:
    components = (profile or {}).get("curriculum_components")
    if not isinstance(components, list) or not components:
        return None
    basis = str((profile or {}).get("curriculum_basis") or "").strip()
    rendered = ", ".join(str(item).strip() for item in components if str(item).strip())
    if not rendered:
        return None
    intro = "No Colegio Horizonte, o Ensino Medio trabalha com estas materias e componentes:"
    if segment_hint and "medio" not in _normalize_text(segment_hint):
        intro = "No Colegio Horizonte, a base curricular publica inclui estes componentes:"
    answer = f"{intro} {rendered}."
    if basis:
        answer += f" A base curricular segue {basis}"
    return answer


def _academic_policy(profile: dict[str, Any] | None) -> dict[str, Any] | None:
    policy = (profile or {}).get("academic_policy")
    return policy if isinstance(policy, dict) else None


def _render_decimal_label(value: Any, *, suffix: str = "") -> str:
    amount = Decimal(str(value or "0")).quantize(Decimal("0.1"))
    rendered = str(amount).replace(".", ",")
    return f"{rendered}{suffix}"


def _compose_project_of_life_answer(profile: dict[str, Any] | None) -> str | None:
    policy = _academic_policy(profile)
    summary = str((policy or {}).get("project_of_life_summary") or "").strip()
    if not summary:
        highlights = (profile or {}).get("highlights")
        if isinstance(highlights, list):
            for item in highlights:
                if not isinstance(item, dict):
                    continue
                title = _normalize_text(item.get("title"))
                description = str(item.get("description") or "").strip()
                if "projeto de vida" in title and description:
                    summary = description
                    break
    if not summary:
        return None
    return f"No Colegio Horizonte, Projeto de vida e parte da proposta pedagogica. {summary}"


def _compose_attendance_policy_answer(profile: dict[str, Any] | None, *, message: str) -> str | None:
    policy = _academic_policy(profile)
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else None
    if not isinstance(attendance, dict):
        return None
    minimum = _render_decimal_label(attendance.get("minimum_attendance_percent"), suffix="%")
    first_absence = str(attendance.get("first_absence_guidance") or "").strip()
    chronic = str(attendance.get("chronic_absence_guidance") or "").strip()
    follow_up = str(attendance.get("follow_up_channel") or "").strip()
    notes = str(attendance.get("notes") or "").strip()
    normalized = _normalize_text(message)
    if "primeira aula" in normalized and first_absence:
        answer = first_absence
        if follow_up:
            answer += f" Se a situacao se repetir, o acompanhamento costuma passar por {follow_up}."
        return answer
    if any(
        term in normalized
        for term in {"metade das aulas", "75%", "abaixo de 75", "limite de faltas", "frequencia minima", "frequência mínima"}
    ) and chronic:
        answer = f"No Colegio Horizonte, a referencia publica minima de frequencia e {minimum} por componente. {chronic}"
        if notes:
            answer += f" {notes}"
        return answer
    if chronic:
        answer = f"No Colegio Horizonte, a referencia publica minima de frequencia e {minimum} por componente. {chronic}"
        if notes:
            answer += f" {notes}"
        return answer
    return None


def _compose_passing_policy_answer(profile: dict[str, Any] | None, *, authenticated: bool) -> str | None:
    policy = _academic_policy(profile)
    passing = policy.get("passing_policy") if isinstance(policy, dict) else None
    if not isinstance(passing, dict):
        return None
    target = _render_decimal_label(passing.get("passing_average"))
    scale = str(passing.get("reference_scale") or "0-10").strip()
    support = str(passing.get("recovery_support") or "").strip()
    notes = str(passing.get("notes") or "").strip()
    answer = f"No Colegio Horizonte, a referencia publica de aprovacao e media {target}/{scale.split('-')[-1]}."
    if support:
        answer += f" {support}"
    if notes:
        answer += f" {notes}"
    if authenticated:
        answer += " Se quiser, eu posso calcular quanto falta para Lucas ou Ana em uma disciplina especifica."
    return answer


def _parse_public_datetime(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    normalized = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _format_public_date(value: Any) -> str:
    parsed = _parse_public_datetime(value)
    if parsed is None:
        raw = str(value or "").strip()
        return raw or "--"
    return parsed.strftime("%d/%m/%Y")


def _calendar_event_search_blob(item: dict[str, Any]) -> str:
    return _normalize_text(" ".join(str(item.get(key) or "") for key in ("title", "description", "category", "audience")))


def _render_calendar_event_lines(events: list[dict[str, Any]], *, limit: int = 5) -> list[str]:
    rendered: list[str] = []
    for item in events[:limit]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "Evento publico").strip()
        starts_at = _format_public_date(item.get("starts_at"))
        audience = str(item.get("audience") or "").strip()
        description = str(item.get("description") or "").strip()
        suffix = f" · publico: {audience}" if audience else ""
        line = f"- {title} ({starts_at}){suffix}."
        if description:
            line += f" {description}"
        rendered.append(line.strip())
    return rendered


def _compose_calendar_week_answer(events: list[dict[str, Any]]) -> str | None:
    if not events:
        return None
    family_events = [
        item
        for item in events
        if isinstance(item, dict)
        and any(term in _calendar_event_search_blob(item) for term in {"familias", "famílias", "responsaveis", "responsáveis", "pais"})
    ]
    chosen = family_events or [item for item in events if isinstance(item, dict)]
    lines = _render_calendar_event_lines(chosen, limit=4)
    if not lines:
        return None
    return "Os principais eventos publicos para familias e responsaveis nesta base sao:\n" + "\n".join(lines)


def _compose_first_bimester_answer(entries: list[dict[str, Any]], events: list[dict[str, Any]]) -> str | None:
    lines: list[str] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        summary = str(item.get("summary") or "").strip()
        if summary:
            lines.append(f"- {summary}")
    first_term_events = [
        item
        for item in events
        if isinstance(item, dict)
        and (parsed := _parse_public_datetime(item.get("starts_at"))) is not None
        and parsed.date() <= date(2026, 4, 30)
    ]
    lines.extend(_render_calendar_event_lines(first_term_events, limit=4))
    if not lines:
        return None
    return "Linha do tempo publica do primeiro bimestre:\n" + "\n".join(lines[:6])


def _compose_eval_calendar_answer(events: list[dict[str, Any]]) -> str | None:
    matching = [
        item
        for item in events
        if isinstance(item, dict)
        and any(term in _calendar_event_search_blob(item) for term in {"reuniao", "reunião", "simulado", "prova", "plantao", "plantão"})
    ]
    lines = _render_calendar_event_lines(matching or events, limit=6)
    if not lines:
        return None
    return "No calendario publico atual, estes sao os marcos mais relevantes para reunioes, simulados e semanas de prova:\n" + "\n".join(lines)


def _compose_travel_planning_answer(entries: list[dict[str, Any]], events: list[dict[str, Any]]) -> str | None:
    milestones: list[str] = []
    for item in entries:
        if not isinstance(item, dict):
            continue
        summary = str(item.get("summary") or "").strip()
        if summary:
            milestones.append(f"- {summary}")
    relevant_events = [
        item
        for item in events
        if isinstance(item, dict)
        and any(term in _calendar_event_search_blob(item) for term in {"reuniao", "reunião", "simulado", "prova", "familias", "famílias", "responsaveis", "responsáveis"})
    ]
    milestones.extend(_render_calendar_event_lines(relevant_events, limit=5))
    if not milestones:
        return None
    return (
        "Para planejar uma viagem sem atrapalhar a vida escolar, vale observar estes marcos publicos antes de fechar datas:\n"
        + "\n".join(milestones[:7])
    )


def _compose_year_three_phases_answer(entries: list[dict[str, Any]], events: list[dict[str, Any]]) -> str | None:
    admissions = next((item for item in entries if isinstance(item, dict) and "matricula" in _normalize_text(item.get("title"))), None)
    school_year = next((item for item in entries if isinstance(item, dict) and "aulas" in _normalize_text(item.get("summary"))), None)
    closure = next((item for item in entries if isinstance(item, dict) and "formatura" in _normalize_text(item.get("title"))), None)
    routine_events = _render_calendar_event_lines([item for item in events if isinstance(item, dict)], limit=3)
    parts: list[str] = []
    if isinstance(admissions, dict):
        parts.append(f"Admissao: {str(admissions.get('summary') or '').strip()}")
    if isinstance(school_year, dict):
        routine = str(school_year.get("summary") or "").strip()
        if routine_events:
            routine += " Eventos publicos ao longo do ano incluem " + "; ".join(
                line.removeprefix("- ").rstrip(".") for line in routine_events[:2]
            ) + "."
        parts.append(f"Rotina academica: {routine}")
    if isinstance(closure, dict):
        parts.append(f"Fechamento: {str(closure.get('summary') or '').strip()}")
    if parts:
        parts.append(
            "Em ordem pratica, primeiro entra a admissao, depois a rotina academica e, por fim, o fechamento."
        )
    return "\n".join(parts) if parts else None
