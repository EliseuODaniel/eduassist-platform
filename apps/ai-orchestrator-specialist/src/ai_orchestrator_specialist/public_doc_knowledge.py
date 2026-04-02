from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import re
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _public_doc_path(filename: str) -> Path:
    return _repo_root() / "data" / "corpus" / "public" / filename


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        _, _, remainder = text.partition("\n---\n")
        return remainder
    return text


def _normalize_space(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(text or "").strip())
    return cleaned.strip()


@lru_cache(maxsize=64)
def _load_public_doc(filename: str) -> str:
    path = _public_doc_path(filename)
    if not path.exists():
        return ""
    return _strip_frontmatter(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=64)
def _load_sections(filename: str) -> dict[str, str]:
    text = _load_public_doc(filename)
    if not text:
        return {}
    sections: dict[str, str] = {}
    current = "_intro"
    buffer: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if buffer:
                sections[current] = _normalize_space("\n".join(buffer))
            current = _normalize_space(line.removeprefix("## ")).lower()
            buffer = []
            continue
        if line.startswith("# "):
            continue
        buffer.append(line)
    if buffer:
        sections[current] = _normalize_space("\n".join(buffer))
    return sections


def _section(filename: str, heading: str) -> str:
    return _load_sections(filename).get(_normalize_space(heading).lower(), "")


def _safe_sentence(text: str) -> str:
    normalized = _normalize_space(text)
    if not normalized:
        return ""
    if normalized.endswith("."):
        return normalized
    return f"{normalized}."


def _first_line(text: str) -> str:
    normalized = _normalize_space(text)
    if not normalized:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", normalized, maxsplit=1)
    return _safe_sentence(parts[0])


def _render_decimal(value: Any, fallback: str) -> str:
    rendered = str(value or "").strip()
    if not rendered:
        return fallback
    return rendered.replace(".", ",")


def compose_public_academic_policy_overview(profile: dict[str, Any] | None) -> str | None:
    policy = (profile or {}).get("academic_policy") if isinstance(profile, dict) else None
    evaluation = _section("politica-avaliacao-recuperacao-e-promocao.md", "Avaliacao continua")
    feedback = _section("politica-avaliacao-recuperacao-e-promocao.md", "Registro e devolutiva")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    promotion = _section("politica-avaliacao-recuperacao-e-promocao.md", "Promocao e decisao final")
    if not any((evaluation, feedback, recovery, second_call, promotion)):
        return None
    passing = policy.get("passing_policy") if isinstance(policy, dict) else {}
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else {}
    average = _render_decimal(getattr(passing, "get", lambda *_: None)("passing_average"), "7,0")
    minimum_attendance = _render_decimal(getattr(attendance, "get", lambda *_: None)("minimum_attendance_percent"), "75,0")
    return " ".join(
        part
        for part in (
            _first_line(evaluation),
            _first_line(feedback),
            _first_line(recovery),
            _first_line(second_call),
            f"Na referencia publica atual, a escola trabalha com media {average}/10 e frequencia minima de {minimum_attendance}% por componente.",
            _first_line(promotion),
        )
        if part
    ).strip()


def compose_public_conduct_frequency_punctuality(profile: dict[str, Any] | None) -> str | None:
    manual_punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    manual_conduct = _section("manual-regulamentos-gerais.md", "Convivencia e respeito")
    manual_justifications = _section("manual-regulamentos-gerais.md", "Avaliacoes e justificativas")
    policy = (profile or {}).get("academic_policy") if isinstance(profile, dict) else None
    attendance = policy.get("attendance_policy") if isinstance(policy, dict) else {}
    minimum_attendance = _render_decimal(getattr(attendance, "get", lambda *_: None)("minimum_attendance_percent"), "75,0")
    chronic = str(getattr(attendance, "get", lambda *_: None)("chronic_absence_guidance") or "").strip()
    if not any((manual_punctuality, manual_conduct, manual_justifications, chronic)):
        return None
    return " ".join(
        part
        for part in (
            _first_line(manual_punctuality),
            _first_line(manual_conduct),
            _first_line(manual_justifications),
            f"A politica publica de frequencia reforca presenca minima de {minimum_attendance}% por componente e alerta academico quando a recorrencia de faltas compromete a aprovacao.",
            _first_line(chronic),
        )
        if part
    ).strip()


def compose_public_bolsas_and_processes(profile: dict[str, Any] | None) -> str | None:
    edital = {
        "abrangencia": _section("edital-bolsas-e-descontos-2026.md", "Abrangencia"),
        "inscricao": _section("edital-bolsas-e-descontos-2026.md", "Inscricao"),
        "analise": _section("edital-bolsas-e-descontos-2026.md", "Analise"),
        "manutencao": _section("edital-bolsas-e-descontos-2026.md", "Manutencao"),
    }
    rematricula = {
        "rematricula": _section("rematricula-transferencia-e-cancelamento-2026.md", "Rematricula interna"),
        "transfer_in": _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de entrada"),
        "transfer_out": _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de saida"),
        "cancelamento": _section("rematricula-transferencia-e-cancelamento-2026.md", "Cancelamento contratual"),
        "prazos": _section("rematricula-transferencia-e-cancelamento-2026.md", "Prazos de emissao"),
    }
    if not any((*edital.values(), *rematricula.values())):
        return None
    return " ".join(
        part
        for part in (
            _first_line(edital["abrangencia"]),
            _first_line(edital["inscricao"]),
            _first_line(edital["analise"]),
            _first_line(edital["manutencao"]),
            _first_line(rematricula["rematricula"]),
            _first_line(rematricula["transfer_in"]),
            _first_line(rematricula["transfer_out"]),
            _first_line(rematricula["cancelamento"]),
            _first_line(rematricula["prazos"]),
        )
        if part
    ).strip()


def compose_public_health_second_call() -> str | None:
    attested = _section("protocolo-saude-medicacao-e-emergencias.md", "Atestados e justificativas")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    if not attested and not second_call:
        return None
    return " ".join(part for part in (_first_line(attested), _first_line(second_call)) if part).strip()


def compose_public_permanence_and_family_support(profile: dict[str, Any] | None) -> str | None:
    support = _section("orientacao-apoio-e-vida-escolar.md", "Apoio ao estudante")
    mentoring = _section("orientacao-apoio-e-vida-escolar.md", "Reforco e monitoria")
    family = _section("orientacao-apoio-e-vida-escolar.md", "Comunicacao com responsaveis")
    attendance = _section("politica-avaliacao-recuperacao-e-promocao.md", "Frequencia minima")
    project = str((((profile or {}).get("academic_policy") or {}).get("project_of_life_summary")) or "").strip()
    if not any((support, mentoring, family, attendance, project)):
        return None
    return " ".join(
        part
        for part in (
            "Para a familia acompanhar permanencia, apoio e vida escolar sem se perder, a escola combina orientacao, monitorias, comunicacao recorrente e acompanhamento de frequencia.",
            _first_line(support),
            _first_line(mentoring),
            _first_line(family),
            _first_line(attendance),
            _first_line(project),
        )
        if part
    ).strip()


def compose_public_health_authorizations_bridge() -> str | None:
    medication = _section("protocolo-saude-medicacao-e-emergencias.md", "Medicacao de uso eventual")
    emergencies = _section("protocolo-saude-medicacao-e-emergencias.md", "Emergencias")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    authorization = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Autorizacao")
    restrictions = _section("saidas-pedagogicas-eventos-e-autorizacoes.md", "Restricoes")
    if not any((medication, emergencies, second_call, authorization, restrictions)):
        return None
    return " ".join(
        part
        for part in (
            _first_line(medication),
            _first_line(second_call),
            _first_line(authorization),
            _first_line(restrictions),
            _first_line(emergencies),
        )
        if part
    ).strip()


def compose_public_first_month_risks(profile: dict[str, Any] | None) -> str | None:
    docs = _section("secretaria-documentacao-e-prazos.md", "Canais para documentos")
    timelines = _section("secretaria-documentacao-e-prazos.md", "Prazos tipicos")
    credentials = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Credenciais pessoais")
    linkage = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Vinculo com o Telegram")
    support = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Recuperacao e suporte")
    punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    if not any((docs, timelines, credentials, linkage, support, punctuality)):
        return None
    return " ".join(
        part
        for part in (
            "No primeiro mes, os riscos operacionais mais claros sao perder prazo documental, ficar com cadastro desatualizado, usar credenciais de forma insegura ou ignorar alertas de frequencia e pontualidade.",
            "Na pratica, isso compromete credenciais, documentacao e a rotina escolar da familia logo nas primeiras semanas.",
            _first_line(docs),
            _first_line(timelines),
            _first_line(credentials),
            _first_line(linkage),
            _first_line(support),
            _first_line(punctuality),
        )
        if part
    ).strip()


def compose_public_process_compare() -> str | None:
    rematricula = _section("rematricula-transferencia-e-cancelamento-2026.md", "Rematricula interna")
    transfer_in = _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de entrada")
    transfer_out = _section("rematricula-transferencia-e-cancelamento-2026.md", "Transferencia de saida")
    cancelamento = _section("rematricula-transferencia-e-cancelamento-2026.md", "Cancelamento contratual")
    prazos = _section("rematricula-transferencia-e-cancelamento-2026.md", "Prazos de emissao")
    if not any((rematricula, transfer_in, transfer_out, cancelamento, prazos)):
        return None
    return " ".join(
        part
        for part in (
            f"Rematricula: {_first_line(rematricula)}",
            f"Transferencia de entrada: {_first_line(transfer_in)}",
            f"Transferencia de saida: {_first_line(transfer_out)}",
            f"Cancelamento: {_first_line(cancelamento)}",
            f"Prazos e documentos: {_first_line(prazos)}",
        )
        if part
    ).strip()


def compose_public_conduct_frequency_recovery_bridge(profile: dict[str, Any] | None) -> str | None:
    conduct = _section("manual-regulamentos-gerais.md", "Convivencia e respeito")
    punctuality = _section("manual-regulamentos-gerais.md", "Pontualidade e frequencia")
    justifications = _section("manual-regulamentos-gerais.md", "Avaliacoes e justificativas")
    recovery = _section("politica-avaliacao-recuperacao-e-promocao.md", "Recuperacao")
    second_call = _section("politica-avaliacao-recuperacao-e-promocao.md", "Segunda chamada")
    support = _section("orientacao-apoio-e-vida-escolar.md", "Apoio ao estudante")
    if not any((conduct, punctuality, justifications, recovery, second_call, support)):
        return None
    return " ".join(
        part
        for part in (
            "Os documentos publicos tratam disciplina, frequencia e recuperacao como partes do mesmo acompanhamento escolar.",
            _first_line(conduct),
            _first_line(punctuality),
            _first_line(justifications),
            _first_line(second_call),
            _first_line(recovery),
            _first_line(support),
            "Na pratica, faltas, justificativas e postura em sala influenciam quando a escola ativa devolutiva, recomposicao e apoio pedagogico.",
        )
        if part
    ).strip()


def compose_public_transversal_year_bundle() -> str | None:
    communication = _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias")
    support = _section("orientacao-apoio-e-vida-escolar.md", "Comunicacao com responsaveis")
    study = _section("programa-periodo-integral-e-estudo-orientado.md", "Estudo orientado")
    activities = _section("programa-periodo-integral-e-estudo-orientado.md", "Atividades complementares")
    digital = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Vinculo com o Telegram")
    limits = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Limites do canal digital")
    if not any((communication, support, study, activities, digital, limits)):
        return None
    return " ".join(
        part
        for part in (
            "Ao longo do ano, comunicacao com responsaveis, avaliacoes, estudo orientado e canais digitais se reforcam mutuamente.",
            _first_line(communication),
            _first_line(support),
            _first_line(study),
            _first_line(activities),
            _first_line(digital),
            _first_line(limits),
            "Quando ha ajuste de calendario, reforco pedagogico ou nova orientacao, a escola tende a publicar no portal, reforcar pelos canais oficiais e acionar a familia quando o caso exige acompanhamento mais proximo.",
        )
        if part
    ).strip()


def compose_public_calendar_visibility(profile: dict[str, Any] | None) -> str | None:
    public_events = (profile or {}).get("public_calendar_events") if isinstance(profile, dict) else None
    visible_titles: list[str] = []
    if isinstance(public_events, list):
        for item in public_events:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            if title and title not in visible_titles:
                visible_titles.append(title)
    communication = _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias")
    digital_limits = _section("politica-uso-do-portal-aplicativo-e-credenciais.md", "Limites do canal digital")
    visible_preview = ", ".join(visible_titles[:3])
    parts: list[str] = []
    if visible_preview:
        parts.append(
            f"No calendario publico, o que costuma ficar aberto para familias sao marcos gerais como {visible_preview}."
        )
    else:
        parts.append(
            "No calendario publico, o que costuma ficar aberto para familias sao marcos institucionais gerais e eventos coletivos."
        )
    parts.append(
        "O que depende de autenticacao ou contexto interno sao detalhes individuais por aluno, convites direcionados, protocolos, situacoes financeiras e acompanhamentos protegidos."
    )
    if communication:
        parts.append(_first_line(communication))
    if digital_limits:
        parts.append(_first_line(digital_limits))
    return " ".join(part for part in parts if part).strip()


def compose_public_facilities_and_study_support() -> str | None:
    library = _section("servicos-e-espacos-escolares.md", "Nome oficial e atendimento")
    library_services = _section("servicos-e-espacos-escolares.md", "Servicos disponiveis")
    science_lab = _section("servicos-e-espacos-escolares.md", "Laboratorio de ciencias")
    maker_lab = _section("servicos-e-espacos-escolares.md", "Laboratorio de informatica e sala maker")
    study = _section("programa-periodo-integral-e-estudo-orientado.md", "Estudo orientado")
    activities = _section("programa-periodo-integral-e-estudo-orientado.md", "Atividades complementares")
    if not any((library, library_services, science_lab, maker_lab, study, activities)):
        return None
    return " ".join(
        part
        for part in (
            "Biblioteca e laboratorios aparecem como espacos de apoio ao estudo, nao como ambientes isolados do curriculo.",
            _first_line(library),
            _first_line(library_services),
            _first_line(science_lab),
            _first_line(maker_lab),
            _first_line(study),
            _first_line(activities),
            "No ensino medio, isso se conecta a monitorias, pesquisa, cultura digital e projetos praticos no contraturno.",
        )
        if part
    ).strip()


def compose_public_family_new_calendar_assessment_enrollment() -> str | None:
    school_calendar = {
        "start": _section("calendario-letivo-2026.md", "Inicio das aulas"),
        "entry": _section("calendario-letivo-2026.md", "Matricula e ingresso"),
        "family": _section("calendario-letivo-2026.md", "Reunioes com responsaveis"),
    }
    assessments = {
        "regular": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Avaliacoes regulares"),
        "recovery": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Recuperacao paralela"),
        "communication": _section("agenda-avaliacoes-recuperacoes-e-simulados-2026.md", "Comunicacao com as familias"),
    }
    enrollment = {
        "steps": _section("manual-matricula-ensino-medio.md", "Etapas do processo"),
        "documents": _section("manual-matricula-ensino-medio.md", "Documentos exigidos"),
        "digital": _section("manual-matricula-ensino-medio.md", "Envio digital de documentos"),
        "service": _section("manual-matricula-ensino-medio.md", "Atendimento durante a matricula"),
    }
    if not any((*school_calendar.values(), *assessments.values(), *enrollment.values())):
        return None
    return " ".join(
        part
        for part in (
            "Para uma familia nova, os tres documentos cumprem papeis diferentes e complementares.",
            f"Calendario letivo: {_first_line(school_calendar['start'])}",
            f"Ingresso e marcos do ano: {_first_line(school_calendar['entry'])}",
            f"Relacao com a familia: {_first_line(school_calendar['family'])}",
            f"Agenda de avaliacoes: {_first_line(assessments['regular'])}",
            f"Recuperacao e ajustes: {_first_line(assessments['recovery'])}",
            f"Comunicacao com responsaveis: {_first_line(assessments['communication'])}",
            f"Manual de matricula: {_first_line(enrollment['steps'])}",
            f"Documentos e envio: {_first_line(enrollment['documents'])}",
            _first_line(enrollment["digital"]),
            _first_line(enrollment["service"]),
            "Na pratica, uma familia nova usa o manual para entrar corretamente, o calendario para se orientar no ano e a agenda de avaliacoes para nao perder janelas pedagogicas e comunicados importantes.",
        )
        if part
    ).strip()
